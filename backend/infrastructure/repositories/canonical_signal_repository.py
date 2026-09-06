import json
import hashlib
from typing import List, Optional, Dict, Any, Callable
from sqlalchemy.orm import Session
from datetime import datetime
from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.core.postgres import ShadowSignalDB, ShadowProvenanceDB, SignalCorrectionDB
from sqlalchemy import text
import uuid

class CanonicalSignalRepository:
    """
    Workstream 20: Neon Authority.
    Authoritative repository for all Signal Ledger 2.0 operations.
    """
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    async def get_signal_by_id(self, signal_id: str) -> Optional[LiveSignal]:
        with self.session_factory() as pg:
            db_sig = pg.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal_id).first()
            if not db_sig:
                return None
            return self._map_db_to_signal(db_sig)

    async def save_signal(self, signal: LiveSignal) -> None:
        with self.session_factory() as pg:
            db_sig = pg.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal.id).first()
            data = signal.model_dump()

            # 1. Automatic Record Hashing (Phase 20)
            # Hash critical immutable fields
            hash_data = f"{signal.id}|{signal.symbol}|{signal.direction}|{signal.entry_price}|{signal.target_price}|{signal.stop_price}|{signal.strategy_version}"
            data['record_hash'] = hashlib.sha256(hash_data.encode()).hexdigest()
            data['last_updated_at'] = datetime.utcnow()

            # 2. Deep serialize JSON fields
            for col in ['events', 'provenance']:
                val = data.get(col)
                if val is not None and not isinstance(val, str):
                    data[col] = json.dumps(val)

            # Filter data to match DB columns
            db_columns = {c.name for c in ShadowSignalDB.__table__.columns}
            filtered_data = {k: v for k, v in data.items() if k in db_columns}

            if db_sig:
                for k, v in filtered_data.items(): setattr(db_sig, k, v)
            else:
                db_sig = ShadowSignalDB(**filtered_data)
                pg.add(db_sig)
            pg.commit()

    async def get_active_signals(self) -> List[LiveSignal]:
        with self.session_factory() as pg:
            res = pg.query(ShadowSignalDB).filter(
                ShadowSignalDB.status == "ACTIVE"
            ).order_by(ShadowSignalDB.timestamp.desc()).all()
            return [self._map_db_to_signal(r) for r in res]

    async def get_verified_signals(self) -> List[LiveSignal]:
        with self.session_factory() as pg:
            res = pg.query(ShadowSignalDB).filter(
                ShadowSignalDB.outcome_verified == True
            ).order_by(ShadowSignalDB.outcome_timestamp.desc()).all()
            return [self._map_db_to_signal(r) for r in res]

    async def save_provenance(self, provenance: Dict[str, Any]) -> None:
        with self.session_factory() as pg:
            db_prov = ShadowProvenanceDB(
                id=provenance.get('provenance_id', str(uuid.uuid4())),
                signal_id=provenance.get('signal_id'),
                prediction_id=provenance.get('prediction_id'),
                created_at=datetime.utcnow(),
                data_snapshot_timestamp=provenance.get('data_snapshot_timestamp'),
                model_version=provenance.get('model_version'),
                strategy_version=provenance.get('strategy_version'),
                feature_version=provenance.get('feature_version'),
                data_sources=json.dumps(provenance.get('data_sources', {})),
                source_timestamps=json.dumps(provenance.get('source_timestamps', {})),
                input_hash=provenance.get('input_hash'),
                output_hash=provenance.get('output_hash'),
                decision_hash=provenance.get('decision_hash')
            )
            pg.add(db_prov)
            pg.commit()

    async def get_provenance(self, signal_id: str) -> Optional[Dict[str, Any]]:
        with self.session_factory() as pg:
            res = pg.query(ShadowProvenanceDB).filter(ShadowProvenanceDB.signal_id == signal_id).first()
            if not res: return None
            data = {c.name: getattr(res, c.name) for c in res.__table__.columns}
            for col in ['data_sources', 'source_timestamps']:
                if data.get(col): data[col] = json.loads(data[col])
            return data

    def _map_db_to_signal(self, db_obj: ShadowSignalDB) -> LiveSignal:
        data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        # Robust JSON Parsing
        for col in ['events', 'provenance']:
            val = data.get(col)
            if val and isinstance(val, str):
                try: data[col] = json.loads(val)
                except: data[col] = [] if col == 'events' else {}

        if not isinstance(data.get('events'), list): data['events'] = []
        if not isinstance(data.get('provenance'), dict): data['provenance'] = {}

        return LiveSignal(**data)
