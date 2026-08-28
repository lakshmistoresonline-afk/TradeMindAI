
import os
import sys
import json
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.core.database import get_db
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB
from google.api_core import exceptions
import time

class SyncStateManager:
    STATE_FILE = "backend/data/shadow_sync_state.json"

    @staticmethod
    def get_last_sync():
        if os.path.exists(SyncStateManager.STATE_FILE):
            try:
                with open(SyncStateManager.STATE_FILE, 'r') as f:
                    return json.load(f)
            except: pass
        return {"last_signal_ts": "2026-08-18T00:00:00", "last_diag_ts": "2026-08-18T00:00:00"}

    @staticmethod
    def update_last_sync(key, ts):
        state = SyncStateManager.get_last_sync()
        state[key] = ts if isinstance(ts, str) else ts.isoformat()
        os.makedirs(os.path.dirname(SyncStateManager.STATE_FILE), exist_ok=True)
        with open(SyncStateManager.STATE_FILE, 'w') as f:
            json.dump(state, f)

class ShadowSyncService:
    _cooldown_until = 0

    @staticmethod
    async def sync_to_cloud():
        """
        Entry point for background synchronization.
        Wraps the actual sync in a non-blocking task with error handling.
        """
        if time.time() < ShadowSyncService._cooldown_until:
            print(f"[SYNC] In cooldown for {int(ShadowSyncService._cooldown_until - time.time())}s. Skipping.")
            return

        # Fire and forget if called within an existing loop,
        # or run safely if we want to wait without blocking the main engine's core logic.
        try:
            await ShadowSyncService._perform_sync()
        except Exception as e:
            print(f"[SYNC] Unexpected error: {e}")

    @staticmethod
    async def _perform_sync():
        db_client = get_db()
        if not db_client:
            return

        state = SyncStateManager.get_last_sync()
        print("[*] Starting Asynchronous Firestore Mirroring...")

        try:
            with SessionLocal() as session:
                # 1. Summary & Portfolio (Always sync latest state)
                # These are single documents, low impact.
                await ShadowSyncService._sync_summary(session, db_client)
                await ShadowSyncService._sync_portfolio(session, db_client)

                # 2. Incremental Signal Sync
                last_sig_ts = state.get("last_signal_ts")
                new_signals = session.query(ShadowSignalDB).filter(
                    # Sync if new OR if recently updated (outcome etc)
                    # For simplicity, we sync signals with timestamp >= last_sig_ts - 24h to catch updates
                    ShadowSignalDB.timestamp >= (datetime.fromisoformat(last_sig_ts) - timedelta(days=1))
                ).all()

                if new_signals:
                    await ShadowSyncService._mirror_signals(new_signals, db_client)
                    SyncStateManager.update_last_sync("last_signal_ts", datetime.utcnow().isoformat())

                # 3. Incremental Diagnostics (Limited Frequency)
                # Only sync the absolute latest scan diagnostics to avoid quota death.
                await ShadowSyncService._mirror_latest_diagnostics(session, db_client)

                print("[SUCCESS] Firestore Mirroring Cycle Complete.")

        except exceptions.ResourceExhausted:
            print("[!!] Firestore QUOTA EXCEEDED (429). Entering 1-hour cooldown.")
            ShadowSyncService._cooldown_until = time.time() + 3600
        except Exception as e:
            print(f"[!] Firestore Sync Error: {e}")

    @staticmethod
    async def _sync_summary(session, db_client):
        from backend.services.market_calendar import IndianMarketCalendar
        session_type = IndianMarketCalendar.get_current_session(datetime.utcnow())

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

        # Accounting (10% allocation model)
        allocation = 100000.0
        total_realized_pnl = round(sum([allocation * (r / 100.0) for r in returns]), 2)

        summary = {
            "strategy": "trademind-equity-v2.2",
            "baseline_start": "2026-08-18",
            "evaluation_cycles": eval_cycles,
            "evaluation_events": eval_events,
            "eligible_evaluations": eval_cycles * 196,
            "transactional_signals": transactional_signals,
            "active_positions": active_signals_count,
            "completed_trades": completed_trades,
            "trade_count": completed_trades,
            "win_rate": round(wins/completed_trades*100, 2) if completed_trades > 0 else 0.0,
            "wins": wins,
            "net_ev": round(avg_return, 4),
            "last_run": datetime.utcnow().isoformat(),
            "equity": round(1000000.0 + total_realized_pnl, 2),
            "realized_pnl": total_realized_pnl,
            "market_status": session_type # Mirror current session state
        }
        db_client.collection("shadow_summary").document("latest").set(summary, timeout=5)

    @staticmethod
    async def _sync_portfolio(session, db_client):
        # Mirror current equity to the expected portfolio path
        # Fetch latest summary info
        terminal = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'TIMEOUT'])).all()
        returns = [t.net_return for t in terminal if t.net_return is not None]
        allocation = 100000.0
        total_realized_pnl = round(sum([allocation * (r / 100.0) for r in returns]), 2)

        db_client.collection("portfolio").document("equity").set({
            "current_equity": round(1000000.0 + total_realized_pnl, 2),
            "realized_pnl": total_realized_pnl,
            "last_updated": datetime.utcnow().isoformat(),
            "currency": "INR"
        }, timeout=5)

    @staticmethod
    async def _mirror_signals(signals, db_client):
        # Use batches for efficiency
        batch = db_client.batch()
        for s in signals:
            sig_data = {
                "id": s.id, "symbol": s.symbol, "direction": s.direction,
                "timestamp": s.timestamp.isoformat() if isinstance(s.timestamp, datetime) else s.timestamp,
                "created_at": (s.created_at or s.timestamp).isoformat() if isinstance(s.timestamp, datetime) else (s.created_at or s.timestamp),
                "updated_at": (s.updated_at or s.timestamp).isoformat() if isinstance(s.timestamp, datetime) else (s.updated_at or s.timestamp),
                "entry_price": s.entry_price, "target_price": s.target_price, "stop_price": s.stop_price,
                "prob": s.calibrated_probability, "ev": s.expected_value,
                "status": s.status, "net_return": s.net_return,
                "updated_at": datetime.utcnow().isoformat(),
                "model_version": s.model_version,

                # Step 3A Fields
                "universe_version": s.universe_version,
                "evaluation_mode": s.evaluation_mode,
                "signal_eligibility": s.signal_eligibility,
                "data_timestamp": s.data_timestamp.isoformat() if s.data_timestamp else None,
                "market_timestamp": s.market_timestamp.isoformat() if s.market_timestamp else None,
                "exit_reason": s.exit_reason
            }
            sig_ref = db_client.collection("shadow_signals").document(s.id)
            batch.set(sig_ref, sig_data)

        # Commit in a non-blocking way if possible, or just catch errors
        batch.commit(timeout=10)
        print(f"   [SYNC] Mirrored {len(signals)} signals to Firestore.")

    @staticmethod
    async def _mirror_latest_diagnostics(session, db_client):
        # Only mirror the single latest evaluation scan to keep UI fresh without heavy writes
        latest_eval_ts = session.query(func.max(ShadowEventDB.timestamp)).filter(ShadowEventDB.event_type == 'EVALUATION').scalar()
        if not latest_eval_ts: return

        # Check if already synced
        state = SyncStateManager.get_last_sync()
        if state.get("last_diag_ts") == latest_eval_ts.isoformat():
            return

        latest_evals = session.query(ShadowEventDB).filter(
            ShadowEventDB.event_type == 'EVALUATION',
            ShadowEventDB.timestamp == latest_eval_ts
        ).all()

        if not latest_evals: return

        # To save quota, we only push a SAMPLE of diagnostics or a summary if the list is too long
        # But for now, 200 writes once per scan is manageable if we don't do it every few minutes.
        batch = db_client.batch()
        for ev in latest_evals:
            diag_id = f"diag_{ev.symbol}" # Idempotent per symbol (overwrites previous scan)
            diag_ref = db_client.collection("shadow_scan_diagnostics").document(diag_id)
            payload = json.loads(ev.payload_json) if ev.payload_json else {}
            batch.set(diag_ref, {
                "symbol": ev.symbol,
                "scan_timestamp": ev.timestamp.isoformat(),
                "decision": ev.decision,
                "reason": ev.rejection_reason,
                "score": payload.get("prob"),
                "ev": payload.get("ev", 0.0),
                "price": payload.get("price", 0.0),
                "model_version": ev.model_version,
                "evaluation_mode": ev.evaluation_mode
            })
        batch.commit(timeout=15)
        SyncStateManager.update_last_sync("last_diag_ts", latest_eval_ts.isoformat())
        print(f"   [SYNC] Updated latest universe diagnostics ({len(latest_evals)} symbols).")
