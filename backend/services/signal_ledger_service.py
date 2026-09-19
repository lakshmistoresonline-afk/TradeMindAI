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

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        import datetime
        import pandas as pd
        if isinstance(obj, (datetime.datetime, datetime.date, pd.Timestamp)):
            return obj.isoformat()
        return super().default(obj)

class SignalLedgerService:
    """
    Authoritative Signal Ledger Service.
    Neon/Postgres is the authority. Firestore is a mirror.
    """

    @staticmethod
    async def create_signal(signal: LiveSignal, session: Optional[Session] = None) -> LiveSignal:
        """
        Atomically creates a signal in Neon and mirrors to Firestore.
        """
        db = session or SessionLocal()
        try:
            # 1. Neon Persistence
            signal_data = signal.model_dump()

            # Handle JSON fields for SQLAlchemy
            if "provenance" in signal_data and signal_data["provenance"]:
                signal_data["provenance"] = json.dumps(signal_data["provenance"], cls=CustomJSONEncoder)
            if "events" in signal_data and signal_data["events"]:
                signal_data["events"] = json.dumps([e.model_dump() for e in signal.events], cls=CustomJSONEncoder)

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

            # 2. Firestore Mirror (P1 Hardening: Run in thread to avoid blocking loop)
            if db_client:
                import asyncio
                def run_mirror():
                    try:
                        mirror_data = signal.model_dump()
                        mirror_data["mirrored_at"] = datetime.datetime.now(timezone.utc).isoformat()
                        mirror_data["source_neon_id"] = signal.id
                        # Firestore client is often synchronous in python admin SDK
                        db_client.collection("signals").document(signal.id).set(mirror_data)
                    except Exception as e:
                        print(f"[SignalLedger] Mirror failed for {signal.id}: {e}")

                asyncio.create_task(asyncio.to_thread(run_mirror))

            return signal

        except Exception as e:
            db.rollback()
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
                # Only allow updating metadata or events, not core levels or outcomes
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
            # 1. Check Live signals (Active)
            db_obj = db.query(LiveSignalDB).filter(LiveSignalDB.id == signal_id).first()
            if db_obj:
                return container.ios_repo._map_db_to_live_signal(db_obj)

            # 2. Check Shadow signals (History)
            db_obj_h = db.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal_id).first()
            if db_obj_h:
                return container.ios_repo._map_db_to_live_signal(db_obj_h)

            return None
        finally:
            db.close()
