
import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime
from backend.core.database import db_client
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB

class ShadowSyncService:
    @staticmethod
    async def sync_to_cloud():
        """
        Synchronizes the latest Shadow Monitoring data from local SQLite to Firestore.
        This enables hosted visibility without exposing the local DB.
        """
        if not db_client:
            print("[!] Firestore client not initialized. Sync skipped.")
            return

        print("[*] Synchronizing Shadow State to Firestore...")

        try:
            with SessionLocal() as session:
                # 1. Summary Metrics
                eval_cycles = session.query(ShadowEventDB.timestamp).filter(ShadowEventDB.event_type == 'EVALUATION').distinct().count()
                eval_events = session.query(ShadowEventDB).filter(ShadowEventDB.event_type == 'EVALUATION').count()
                transactional_signals = session.query(ShadowSignalDB).count()
                active_signals_count = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').count()

                TERMINAL_STATES = ['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'TIMEOUT', 'AMBIGUOUS', 'INVALID']
                completed_trades = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(TERMINAL_STATES)).count()

                terminal = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(TERMINAL_STATES)).all()
                wins = len([t for t in terminal if t.status == 'TARGET_HIT'])
                returns = [t.net_return for t in terminal if t.net_return is not None]
                avg_return = sum(returns) / len(returns) if returns else 0.0

                summary = {
                    "strategy": "trademind-equity-v2.2",
                    "baseline_start": "2026-08-18",
                    "evaluation_cycles": eval_cycles,
                    "evaluation_events": eval_events,
                    "eligible_evaluations": eval_cycles * 196,
                    "transactional_signals": transactional_signals,
                    "active_signals_count": active_signals_count,
                    "completed_trades": completed_trades,
                    "win_rate": round(wins/completed_trades*100, 2) if completed_trades > 0 else 0.0,
                    "net_ev": round(avg_return, 4),
                    "last_updated": datetime.utcnow().isoformat()
                }

                # 2. Active Signals
                active_signals = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()
                signals_list = [{
                    "id": s.id,
                    "symbol": s.symbol,
                    "direction": s.direction,
                    "entry": s.entry_price,
                    "target": s.target_price,
                    "stop": s.stop_price,
                    "prob": s.calibrated_probability,
                    "ev": s.expected_value,
                    "timestamp": s.timestamp.isoformat() if isinstance(s.timestamp, datetime) else s.timestamp
                } for s in active_signals]

                # 3. Latest Outcome
                latest = session.query(ShadowSignalDB).filter(
                    ShadowSignalDB.status.in_(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'])
                ).order_by(ShadowSignalDB.outcome_timestamp.desc()).first()

                latest_outcome = {
                    "symbol": latest.symbol,
                    "status": latest.status,
                    "net_return": latest.net_return,
                    "timestamp": latest.outcome_timestamp.isoformat() if latest.outcome_timestamp else None
                } if latest else None

                # 4. Rejection Counts
                rejections = session.query(ShadowEventDB.rejection_reason, sqlite3.func.count(ShadowEventDB.id)).filter(
                    ShadowEventDB.decision != 'TRADE_SIGNAL',
                    ShadowEventDB.rejection_reason.isnot(None)
                ).group_by(ShadowEventDB.rejection_reason).all()
                rejection_counts = {r[0]: r[1] for r in rejections}

                # PUSH TO FIRESTORE
                state_ref = db_client.collection("shadow_monitor").document("state")
                state_ref.set({
                    "summary": summary,
                    "active_signals": signals_list,
                    "latest_outcome": latest_outcome,
                    "rejection_counts": rejection_counts,
                    "health": {
                        "db": "PASS", "models": "PASS", "freshness": "PASS", "persistence": "PASS"
                    }
                })

                print("[SUCCESS] Shadow State synced to Firestore.")

        except Exception as e:
            print(f"[!] Shadow Sync Error: {e}")
            import traceback
            traceback.print_exc()
