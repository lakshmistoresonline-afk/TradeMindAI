import datetime
from typing import Dict, Any, List
from backend.core.postgres import SessionLocal, ShadowSignalDB
from backend.core.database import db_client

class ReconciliationEngine:
    """
    Workstream 18: End-to-End Reconciliation.
    Compares Neon (Authority) vs mirrors and reports mismatches.
    """

    @staticmethod
    async def reconcile_all() -> Dict[str, Any]:
        with SessionLocal() as session:
            # 1. SQL State
            sql_signals = session.query(ShadowSignalDB).all()
            sql_data = {s.id: {
                "status": s.status,
                "net_pnl": float(s.net_pnl) if s.net_pnl is not None else None,
                "record_hash": s.record_hash
            } for s in sql_signals}

            # 2. Firestore State
            if not db_client:
                return {"status": "FAILED", "reason": "FIRESTORE_NOT_CONNECTED"}

            fs_docs = db_client.collection("shadow_signals").get()
            fs_data = {doc.id: doc.to_dict() for doc in fs_docs}

            # 3. Mismatch detection
            mismatches = []
            missing_in_fs = []

            for sid, s_val in sql_data.items():
                if sid not in fs_data:
                    missing_in_fs.append(sid)
                else:
                    f_val = fs_data[sid]
                    if s_val['status'] != f_val.get('status'):
                        mismatches.append({"id": sid, "field": "status", "sql": s_val['status'], "fs": f_val.get('status')})

            return {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "neon_count": len(sql_data),
                "firestore_count": len(fs_data),
                "missing_in_mirror": missing_in_fs,
                "mismatches": mismatches,
                "status": "PASS" if not missing_in_fs and not mismatches else "WARNING"
            }
