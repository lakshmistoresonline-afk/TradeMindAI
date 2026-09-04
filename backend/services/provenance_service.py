import datetime
import json
from typing import Dict, Any, Optional
from backend.core.postgres import SessionLocal, PredictionDB

class ProvenanceService:
    """
    Workstream 8: Provenance View (Why this signal?).
    Retrieves the actual stored evidence for a decision.
    """

    @staticmethod
    def get_signal_provenance(prediction_id: str) -> Dict[str, Any]:
        with SessionLocal() as session:
            pred = session.query(PredictionDB).filter(PredictionDB.id == prediction_id).first()
            if not pred:
                return {"status": "NOT_FOUND"}

            metadata = json.loads(pred.metadata_json) if pred.metadata_json else {}

            return {
                "signal_id": prediction_id,
                "symbol": pred.symbol,
                "timestamp": pred.timestamp.isoformat(),
                "model": pred.model_version,
                "probability": pred.probability,
                "expected_value": pred.expected_value,
                "regime": pred.regime,
                "input_snapshot": metadata
            }
