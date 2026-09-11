import datetime
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
            db.commit()
            db.refresh(db_obj)

            # 2. Firestore Mirror
            if db_client:
                try:
                    mirror_data = signal.model_dump()
                    # Add mirror metadata
                    mirror_data["mirrored_at"] = datetime.datetime.utcnow()
                    mirror_data["source_neon_id"] = signal.id

                    db_client.collection("signals").document(signal.id).set(mirror_data)
                except Exception as e:
                    print(f"[SignalLedger] Mirror failed for {signal.id}: {e}")

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

            for key, value in updates.items():
                if hasattr(db_obj, key):
                    if key in ["provenance", "events"] and isinstance(value, (dict, list)):
                        setattr(db_obj, key, json.dumps(value))
                    else:
                        setattr(db_obj, key, value)

            db_obj.updated_at = datetime.datetime.utcnow()
            db.commit()

            # Mirror to Firestore
            if db_client:
                try:
                    db_client.collection("signals").document(signal_id).update(updates)
                except Exception as e:
                    print(f"[SignalLedger] Mirror update failed for {signal_id}: {e}")

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
            if not db_obj:
                return None

            # Convert back to Domain model
            data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
            if data.get("provenance"): data["provenance"] = json.loads(data["provenance"])
            if data.get("events"): data["events"] = json.loads(data["events"])

            return LiveSignal(**data)
        finally:
            db.close()
