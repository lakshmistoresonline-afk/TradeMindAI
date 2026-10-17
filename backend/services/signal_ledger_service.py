import datetime
from datetime import timezone
import uuid

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.core.postgres import LiveSignalDB, ShadowSignalDB, SessionLocal
from backend.core.database import db_client
from backend.domain.models.ios import LiveSignal
from backend.core.container import container
from backend.services.signal_eligibility import is_eligible_buy

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        import datetime
        import pandas as pd
        if isinstance(obj, (datetime.datetime, datetime.date, pd.Timestamp)):
            return obj.isoformat()
        return super().default(obj)

class SignalLedgerService:
    """
    Authoritative Signal Ledger Service (Atomic Idempotency & BUY-Only Enforced).
    Neon/Postgres is the authority. Firestore is a mirror.
    """

    @staticmethod
    async def create_signal(signal: LiveSignal, session: Optional[Session] = None) -> LiveSignal:
        """
        Atomically creates a signal in Neon and mirrors to Firestore.
        Enforces BUY-only eligibility and persistence-level idempotency by symbol and timeframe,
        allowing distinct horizons (SHORT, SWING, LONG) to coexist.
        """
        if not is_eligible_buy(signal):
            raise ValueError("Signal violates BUY-only eligibility policy and cannot be persisted.")

        db = session or SessionLocal()
        try:
            tf = getattr(signal, "timeframe", None)
            if not tf and hasattr(signal, "decision") and signal.decision:
                tf = getattr(signal.decision, "timeframe", "SWING")
            if not tf:
                tf = "SWING"

            # Check for existing active duplicate for same symbol and timeframe (idempotency)
            existing = db.query(LiveSignalDB).filter(
                LiveSignalDB.symbol == signal.symbol,
                LiveSignalDB.timeframe == tf,
                LiveSignalDB.status == "ACTIVE"
            ).first()
            if existing:
                print(f"[SignalLedger] Idempotency: Active signal for {signal.symbol} ({tf}) already exists. Returning existing record.")
                return container.ios_repo._map_db_to_live_signal(existing)

            # 1. Neon Persistence
            signal_data = signal.model_dump()

            # Handle JSON fields for SQLAlchemy
            if "provenance" in signal_data and signal_data["provenance"]:
                if isinstance(signal_data["provenance"], dict):
                    signal_data["provenance"] = json.dumps(signal_data["provenance"], cls=CustomJSONEncoder)
            else:
                signal_data["provenance"] = json.dumps({}, cls=CustomJSONEncoder)

            if "events" in signal_data:
                evs = signal_data["events"]
                if isinstance(evs, list):
                    signal_data["events"] = json.dumps([e.model_dump() if hasattr(e, "model_dump") else e for e in evs], cls=CustomJSONEncoder)
                else:
                    signal_data["events"] = json.dumps([], cls=CustomJSONEncoder)
            else:
                signal_data["events"] = json.dumps([], cls=CustomJSONEncoder)

            db_obj = LiveSignalDB(**{k: v for k, v in signal_data.items() if hasattr(LiveSignalDB, k)})
            db.add(db_obj)

            # 1.5 Provenance Enforcement (Audit Phase 1.3)
            if signal.provenance:
                from backend.core.postgres import ShadowProvenanceDB
                prov = signal.provenance
                prov_obj = ShadowProvenanceDB(
                    id=prov.get("provenance_id", str(uuid.uuid4())),
                    signal_id=signal.id,
                    prediction_id=signal.prediction_id,
                    data_snapshot_timestamp=prov.get("data_snapshot_timestamp"),
                    model_version=prov.get("model_version"),
                    strategy_version=prov.get("strategy_version", "v2.2"),
                    feature_version=prov.get("feature_version"),
                    data_sources=json.dumps(prov.get("data_sources")),
                    source_timestamps=json.dumps(prov.get("source_timestamps")),
                    input_hash=prov.get("input_hash"),
                    output_hash=prov.get("output_hash"),
                    decision_hash=prov.get("decision_hash")
                )
                db.add(prov_obj)

            db.commit()
            db.refresh(db_obj)

            # 2. Firestore Mirror (Only on genuine new successful PostgreSQL insertion)
            if db_client:
                import asyncio
                def run_mirror():
                    try:
                        mirror_data = signal.model_dump()
                        mirror_data["mirrored_at"] = datetime.datetime.now(timezone.utc).isoformat()
                        mirror_data["source_neon_id"] = signal.id
                        db_client.collection("signals").document(signal.id).set(mirror_data)
                    except Exception as e:
                        print(f"[SignalLedger] Mirror failed for {signal.id}: {e}")

                asyncio.create_task(asyncio.to_thread(run_mirror))

            return signal

        except Exception as e:
            db.rollback()
            err_str = str(e).lower()
            is_unique_violation = (
                "unique constraint failed" in err_str or
                "integrityerror" in type(e).__name__.lower() or
                "duplicate key value violates unique constraint" in err_str or
                "idx_unique_active_signal" in err_str
            )
            if is_unique_violation:
                tf = getattr(signal, "timeframe", None)
                if not tf and hasattr(signal, "decision") and signal.decision:
                    tf = getattr(signal.decision, "timeframe", "SWING")
                if not tf:
                    tf = "SWING"

                existing = db.query(LiveSignalDB).filter(
                    LiveSignalDB.symbol == signal.symbol,
                    LiveSignalDB.timeframe == tf,
                    LiveSignalDB.status == "ACTIVE"
                ).first()
                if existing:
                    print(f"[SignalLedger] Precise atomic idempotency: Duplicate active signal for {signal.symbol} ({tf}) caught via DB constraint. Returning existing persisted record.")
                    return container.ios_repo._map_db_to_live_signal(existing)

            # Unrelated integrity errors propagate normally and are not swallowed
            raise e
        finally:
            if not session:
                db.close()

    @staticmethod
    async def update_signal(signal_id: str, updates: Dict[str, Any], session: Optional[Session] = None) -> bool:
        """
        Updates a signal in Neon and syncs to Firestore.
        """
        db = session or SessionLocal()
        try:
            db_obj = db.query(LiveSignalDB).filter(LiveSignalDB.id == signal_id).first()
            if not db_obj:
                return False

            # 1. Immutability Protection (Phase 3 Final Truth Lock)
            TERMINAL_STATES = ["TARGET_HIT", "STOP_LOSS", "EXPIRED", "CANCELLED", "AMBIGUOUS"]
            if db_obj.status in TERMINAL_STATES:
                RESTRICTED_FIELDS = [
                    "symbol", "direction", "asset_class", "instrument_id",
                    "entry_price", "target_price", "stop_price", "profit_pct",
                    "status", "outcome_date", "exit_price", "realized_return",
                    "decision_timestamp", "strategy_version", "signal_version",
                    "model_id", "model_version", "model_hash", "feature_version",
                    "feature_hash", "prediction_id", "provenance_id", "decision_hash"
                ]
                for key in updates:
                    if key in RESTRICTED_FIELDS:
                        print(f"[SignalLedger] Update BLOCKED: Signal {signal_id} is in terminal state {db_obj.status}. Cannot mutate immutable fact: {key}")
                        return False


            for key, value in updates.items():
                if hasattr(db_obj, key):
                    if key in ["provenance", "events"] and isinstance(value, (dict, list)):
                        setattr(db_obj, key, json.dumps(value))
                    else:
                        setattr(db_obj, key, value)

            db_obj.updated_at = datetime.datetime.now(timezone.utc)
            db.commit()

            # Mirror to Firestore (P1 Hardening: Run in thread to avoid blocking loop)
            if db_client:
                import asyncio
                def run_mirror_update():
                    try:
                        db_client.collection("signals").document(signal_id).update(updates)
                    except Exception as e:
                        print(f"[SignalLedger] Mirror update failed for {signal_id}: {e}")

                asyncio.create_task(asyncio.to_thread(run_mirror_update))

            return True

        except Exception as e:
            db.rollback()
            raise e
        finally:
            if not session:
                db.close()

    @staticmethod
    async def get_signal(signal_id: str) -> Optional[LiveSignal]:
        db = SessionLocal()
        try:
            db_obj = db.query(LiveSignalDB).filter(LiveSignalDB.id == signal_id).first()
            if db_obj:
                return container.ios_repo._map_db_to_live_signal(db_obj)

            db_obj_h = db.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal_id).first()
            if db_obj_h:
                return container.ios_repo._map_db_to_live_signal(db_obj_h)

            return None
        finally:
            db.close()
