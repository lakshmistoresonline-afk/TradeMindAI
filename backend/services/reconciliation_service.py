import datetime
from typing import Dict, Any, List
from backend.core.postgres import SessionLocal, LiveSignalDB
from backend.core.database import db_client
from backend.domain.models.ios import LiveSignal

class ReconciliationService:
    """
    Phase 48: End-to-End Master Reconciliation.
    Compares Neon vs Firestore and detects drift.
    """

    @staticmethod
    async def reconcile_neon_firestore() -> Dict[str, Any]:
        """
        Compares signals in Neon with their counterparts in Firestore.
        """
        report = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "total_neon": 0,
            "total_firestore": 0,
            "mismatches": [],
            "missing_in_firestore": [],
            "status": "PASS"
        }

        with SessionLocal() as session:
            neon_signals = session.query(LiveSignalDB).all()
            report["total_neon"] = len(neon_signals)

            if not db_client:
                return {"status": "FAIL", "reason": "FIRESTORE_UNAVAILABLE"}

            for n_sig in neon_signals:
                fs_doc = db_client.collection("signals").document(n_sig.id).get()

                if not fs_doc.exists:
                    report["missing_in_firestore"].append(n_sig.id)
                    continue

                fs_data = fs_doc.to_dict()
                # Check key fields for parity
                fields_to_check = ["status", "entry_price", "target_price", "stop_price"]
                for field in fields_to_check:
                    n_val = getattr(n_sig, field)
                    fs_val = fs_data.get(field)

                    if n_val != fs_val:
                        report["mismatches"].append({
                            "id": n_sig.id,
                            "field": field,
                            "neon": n_val,
                            "firestore": fs_val
                        })
                        report["status"] = "RECONCILIATION_FAIL"

        return report
