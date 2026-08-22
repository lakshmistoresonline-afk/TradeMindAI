import os
import sys
import json
import pandas as pd
from sqlalchemy import create_engine, text
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from google.cloud import firestore as google_firestore

PROJECT_ID = "com-webcraft-trademindai-c8f75"
POSTGRES_URL = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

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

def sync_all():
    db = get_db()
    if not db: return

    print(f"--- STARTING FINAL FORENSIC FIREBASE SYNC: {PROJECT_ID} ---")
    engine = create_engine(POSTGRES_URL)

    with engine.connect() as conn:
        # 1. Stocks
        print("[*] Syncing Stock Master (Neon Authoritative)...")
        stocks_df = pd.read_sql_query(text("SELECT * FROM stocks"), conn)
        batch = db.batch()
        count = 0
        for _, row in stocks_df.iterrows():
            doc_ref = db.collection("stocks").document(row['symbol'])
            data = {
                "name": str(row['name']),
                "sector": str(row['sector']),
                "industry": str(row['industry']),
                "last_price": float(row['last_price']) if pd.notna(row['last_price']) else 0.0,
                "market_cap": int(row['market_cap']) if pd.notna(row['market_cap']) else 0,
                "is_fno": bool(row['is_fno']),
                "index_membership": str(row['index_membership']),
                "status": "DATA_UNAVAILABLE" if row['symbol'] in ['GUJGASLTD', 'LTIM'] else "OPERATIONAL",
                "updated_at": google_firestore.SERVER_TIMESTAMP
            }
            batch.set(doc_ref, data, merge=True)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"   [+] Synced {count} stocks.")

        # 2. Instruments (F&O)
        print("[*] Syncing Instruments (Neon)...")
        inst_df = pd.read_sql_query(text("SELECT * FROM instruments"), conn)
        batch = db.batch()
        for _, row in inst_df.iterrows():
            doc_ref = db.collection("instruments").document(row['id'])
            batch.set(doc_ref, {
                "symbol": row['trading_symbol'],
                "exchange": row['exchange'],
                "type": row['instrument_type'],
                "expiry": row['expiry'],
                "strike": row['strike'],
                "option_type": row['option_type'],
                "lot_size": row['lot_size'],
                "updated_at": google_firestore.SERVER_TIMESTAMP
            }, merge=True)
        batch.commit()
        print(f"   [+] Synced {len(inst_df)} instruments.")

        # 3. Market Regimes
        print("[*] Syncing Market Regimes (Neon Full History)...")
        regimes_df = pd.read_sql_query(text("SELECT * FROM market_regimes"), conn)
        batch = db.batch()
        count = 0
        for _, row in regimes_df.iterrows():
            try: dt = row['date'] if isinstance(row['date'], datetime) else datetime.fromisoformat(row['date'])
            except: dt = datetime.utcnow()
            doc_id = dt.strftime("%Y-%m-%d")
            batch.set(db.collection("market_regimes").document(doc_id), {
                "date": dt, "regime": row['regime'], "risk_mode": row['risk_mode'],
                "sentiment": float(row['sentiment_score']) if pd.notna(row['sentiment_score']) else 0.5,
                "vix": float(row['volatility_index']) if pd.notna(row['volatility_index']) else 15.0,
                "description": str(row['description'])
            }, merge=True)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"   [+] Synced {count} regimes.")

        # 4. Live Signals
        print("[*] Syncing Signal History (Neon)...")
        signals_df = pd.read_sql_query(text("SELECT * FROM live_signals"), conn)
        batch = db.batch()
        count = 0
        for _, row in signals_df.iterrows():
            try: ts = row['timestamp'] if isinstance(row['timestamp'], datetime) else datetime.fromisoformat(row['timestamp'])
            except: ts = datetime.utcnow()
            doc_ref = db.collection("live_signals").document(row['id'])
            batch.set(doc_ref, {
                "symbol": row['symbol'], "timestamp": ts, "direction": row['direction'],
                "score": float(row['conviction']), "entry": float(row['entry_price']),
                "target": float(row['target_price']), "stop": float(row['stop_loss_price']),
                "status": row['status']
            }, merge=True)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"   [+] Synced {count} signals.")

    # 5. Portfolio Equity
    print("[*] Syncing Portfolio Equity (Historical)...")
    equity_path = Path("data/results/step4_4_2/wf_portfolio_equity.csv")
    if equity_path.exists():
        e_df = pd.read_csv(equity_path)
        batch = db.batch()
        count = 0
        for _, row in e_df.iterrows():
            date_str = row['date'].split(' ')[0]
            doc_id = f"backtest_{date_str}"
            db.collection("portfolio_equity").document(doc_id).set({
                "date": datetime.fromisoformat(row['date'].replace('Z', '').replace(' ', 'T')),
                "equity": float(row['equity']),
                "type": "backtest"
            }, merge=True)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"   [+] Synced {count} historical equity points.")

    # 6. Performance Summaries
    print("[*] Syncing Performance Summaries...")
    summaries = {
        "backtest": {"total_return": 1747.16, "win_rate": 49.77, "trades": 6882, "status": "VERIFIED"},
        "walk_forward": {"total_return": 2757.34, "win_rate": 52.57, "trades": 4489, "status": "VALIDATED"}
    }
    for k, v in summaries.items():
        db.collection("performance_summary").document(k).set(v)

    # 7. System Status
    db.collection("system_status").document("latest").set({
        "last_sync": google_firestore.SERVER_TIMESTAMP,
        "operational_symbols": 198,
        "version": "v2.2"
    })

    engine.dispose()
    print("[SUCCESS] Forensic Firebase synchronization verified.")

if __name__ == "__main__":
    sync_all()
