import os
import sys
import json
import pandas as pd
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore as google_firestore
from sqlalchemy import func

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"
load_dotenv('backend/.env')

from backend.services.market_calendar import IndianMarketCalendar

PROJECT_ID = "com-webcraft-trademindai-c8f75"

def get_access_token():
    try:
        token = subprocess.check_output("gcloud auth print-access-token", shell=True).decode('utf-8').strip()
        return token
    except Exception as e:
        print(f"[!!] Failed to get access token: {e}")
        return None

def get_db():
    token = get_access_token()
    if not token: return None
    try:
        from google.oauth2 import credentials as oauth2_credentials
        creds = oauth2_credentials.Credentials(token)
        db = google_firestore.Client(project=PROJECT_ID, credentials=creds)
        return db
    except Exception as e:
        print(f"[!!] Firestore init failed: {e}")
        return None

async def sync_shadow_data():
    db = get_db()
    if not db: return

    print("[*] Synchronizing Shadow Data to Firebase...")

    from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB, ShadowScanDiagnosticDB

    with SessionLocal() as session:
        # 1. Shadow Signals
        signals = session.query(ShadowSignalDB).all()
        batch = db.batch()
        count = 0
        for s in signals:
            doc_ref = db.collection("shadow_signals").document(s.id)
            data = {
                "symbol": s.symbol,
                "timestamp": s.timestamp,
                "direction": s.direction,
                "entry_price": s.entry_price,
                "target_price": s.target_price,
                "stop_price": s.stop_price,
                "prob": s.calibrated_probability,
                "status": s.status,
                "net_return": s.net_return,
                "updated_at": google_firestore.SERVER_TIMESTAMP
            }
            batch.set(doc_ref, data, merge=True)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"   [+] Synced {count} shadow signals.")

        # 2. Shadow Diagnostics
        print("[*] Syncing Shadow Diagnostics...")
        diagnostics = session.query(ShadowScanDiagnosticDB).order_by(ShadowScanDiagnosticDB.scan_timestamp.desc()).limit(400).all()
        batch = db.batch()
        count = 0
        for d in diagnostics:
            ts_str = d.scan_timestamp.isoformat().replace(':','-').replace('.','_')
            doc_id = f"diag_{d.symbol}_{ts_str}"
            doc_ref = db.collection("shadow_scan_diagnostics").document(doc_id)
            data = {
                "symbol": d.symbol,
                "scan_timestamp": d.scan_timestamp,
                "score": float(d.signal_score) if d.signal_score is not None else 0.0,
                "threshold": float(d.threshold),
                "decision": d.signal_decision,
                "reason": d.rejection_reason,
                "age_hours": float(d.data_age_hours) if d.data_age_hours is not None else 0.0,
                "liquidity": d.liquidity_status,
                "freshness": d.stale_data_status,
                "model_version": d.model_version,
                "synced_at": google_firestore.SERVER_TIMESTAMP
            }
            batch.set(doc_ref, data, merge=True)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"   [+] Synced {count} shadow diagnostics.")

        # 3. Shadow Summary
        portfolio_path = Path("data/results/step4_5/shadow_portfolio.json")
        if portfolio_path.exists():
            with open(portfolio_path, 'r') as f:
                p = json.load(f)

            completed = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'])).all()
            wins = len([t for t in completed if t.status == 'TARGET_HIT'])

            latest_scan_ts = session.query(func.max(ShadowScanDiagnosticDB.scan_timestamp)).scalar()
            rejections = session.query(ShadowScanDiagnosticDB.rejection_reason, func.count(ShadowScanDiagnosticDB.id)).filter(
                ShadowScanDiagnosticDB.scan_timestamp == latest_scan_ts,
                ShadowScanDiagnosticDB.signal_decision == 'REJECTED'
            ).group_by(ShadowScanDiagnosticDB.rejection_reason).all()
            rejection_map = {r[0]: r[1] for r in rejections}

            # Market Status (Phase 7)
            now = IndianMarketCalendar.get_current_time_ist()
            current_session = IndianMarketCalendar.get_current_session(now)

            summary = {
                "equity": p["equity"],
                "cash": p["cash"],
                "realized_pnl": p["realized_pnl"],
                "win_rate": (wins / len(completed) * 100) if completed else 0.0,
                "trade_count": len(completed),
                "active_positions": session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').count(),
                "last_run": google_firestore.SERVER_TIMESTAMP,
                "market_status": "OPEN" if current_session == "OPEN" else "CLOSED",
                "session_type": current_session,
                "rejection_breakdown": rejection_map,
                "scanned_symbols": 200
            }
            db.collection("shadow_summary").document("latest").set(summary)

            # Record Equity History
            db.collection("shadow_equity").document(datetime.utcnow().strftime("%Y-%m-%d")).set({
                "date": datetime.utcnow(),
                "equity": p["equity"],
                "realized_pnl": p["realized_pnl"]
            })
            print("[+] Synced shadow summary and equity.")

    print("[SUCCESS] Firebase Shadow Sync Complete.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(sync_shadow_data())
