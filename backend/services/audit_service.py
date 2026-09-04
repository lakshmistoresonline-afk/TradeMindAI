import datetime
import json
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, ShadowEventDB

class AuditService:
    """
    Workstream 12: Audit Trail.
    Records every major state transition.
    """

    @staticmethod
    def record_event(
        event_type: str,
        symbol: str,
        signal_id: Optional[str] = None,
        decision: Optional[str] = None,
        reason: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        mode: str = "LIVE_SHADOW"
    ):
        with SessionLocal() as session:
            event = ShadowEventDB(
                event_type=event_type,
                symbol=symbol,
                signal_id=signal_id,
                timestamp=datetime.datetime.utcnow(),
                decision=decision,
                rejection_reason=reason,
                payload_json=json.dumps(payload) if payload else None,
                evaluation_mode=mode
            )
            session.add(event)
            session.commit()

    @staticmethod
    def get_audit_trail(signal_id: str) -> List[Dict[str, Any]]:
        with SessionLocal() as session:
            events = session.query(ShadowEventDB).filter(ShadowEventDB.signal_id == signal_id).order_by(ShadowEventDB.timestamp.asc()).all()
            return [{
                "type": e.event_type,
                "timestamp": e.timestamp.isoformat(),
                "decision": e.decision,
                "reason": e.rejection_reason,
                "payload": json.loads(e.payload_json) if e.payload_json else {}
            } for e in events]
