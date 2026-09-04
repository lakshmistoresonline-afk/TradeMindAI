import datetime
import json
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, ShadowEventDB

class AuditTrailService:
    """
    Workstream 12: Audit Trail.
    Traceable ID linking from DATA -> AI -> SIGNAL -> OUTCOME.
    """

    @staticmethod
    def record_transition(
        symbol: str,
        from_state: str,
        to_state: str,
        signal_id: Optional[str] = None,
        prediction_id: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        with SessionLocal() as session:
            event = ShadowEventDB(
                event_type="STATE_TRANSITION",
                symbol=symbol,
                signal_id=signal_id,
                timestamp=datetime.datetime.utcnow(),
                decision=f"{from_state}_TO_{to_state}",
                rejection_reason=reason,
                payload_json=json.dumps({
                    "prediction_id": prediction_id,
                    **(metadata or {})
                }),
                evaluation_mode="LIVE_SHADOW"
            )
            session.add(event)
            session.commit()

    @staticmethod
    def get_full_trace(signal_id: str) -> List[Dict[str, Any]]:
        with SessionLocal() as session:
            # 1. Fetch signal events
            events = session.query(ShadowEventDB).filter(
                ShadowEventDB.signal_id == signal_id
            ).order_by(ShadowEventDB.timestamp.asc()).all()

            trace = []
            for e in events:
                trace.append({
                    "id": e.id,
                    "type": e.event_type,
                    "timestamp": e.timestamp.isoformat(),
                    "payload": json.loads(e.payload_json) if e.payload_json else {}
                })
            return trace
