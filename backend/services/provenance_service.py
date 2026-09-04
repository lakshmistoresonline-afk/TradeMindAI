import datetime
import json
import uuid
import hashlib
from typing import Dict, Any, Optional
from backend.core.container import container

class ProvenanceService:
    """
    Workstream 9: Provenance System.
    Records exactly what was known when a signal was generated.
    """

    @staticmethod
    async def create_provenance(
        signal_id: str,
        prediction_id: str,
        model_version: str,
        strategy_version: str,
        feature_version: str,
        data_snapshot: Dict[str, Any]
    ) -> str:
        provenance_id = f"prov_{uuid.uuid4().hex[:12]}"

        # 1. Create source timestamps
        source_ts = {
            "market_data": datetime.utcnow().isoformat(),
            "snapshot_data": data_snapshot.get('timestamp', datetime.utcnow().isoformat())
        }

        # 2. Calculate hashes for immutability
        input_str = json.dumps(data_snapshot, sort_keys=True)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()

        provenance = {
            "provenance_id": provenance_id,
            "signal_id": signal_id,
            "prediction_id": prediction_id,
            "data_snapshot_timestamp": datetime.utcnow(),
            "model_version": model_version,
            "strategy_version": strategy_version,
            "feature_version": feature_version,
            "data_sources": {"price": "YAHOO_FINANCE", "indicators": "DUCKDB_ANALYTICAL"},
            "source_timestamps": source_ts,
            "input_hash": input_hash,
            "output_hash": "PENDING",
            "decision_hash": hashlib.sha256(signal_id.encode()).hexdigest()
        }

        await container.canonical_signal_repo.save_provenance(provenance)
        return provenance_id

    @staticmethod
    async def get_provenance_dossier(signal_id: str) -> Optional[Dict[str, Any]]:
        return await container.canonical_signal_repo.get_provenance(signal_id)
