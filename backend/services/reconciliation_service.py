import datetime
from typing import Dict, Any, List
from sqlalchemy import func, text
from backend.core.postgres import SessionLocal, ShadowSignalDB
from backend.core.database import db_client

class ReconciliationService:
    """
    Workstream 12: Production Reconciliation Service.
    Compares Authoritative SQL with Mirror Tier (Firestore).
    """

    @staticmethod
    async def run_shadow_reconciliation() -> Dict[str, Any]:
        with SessionLocal() as session:
            # 1. SQL State
            sql_signals = session.query(ShadowSignalDB).all()
            sql_map = {s.id: s.status for s in sql_signals}

            # 2. Firestore State
            if not db_client:
                return {"status": "FAILED", "reason": "FIRESTORE_NOT_CONNECTED"}

            fs_signals = db_client.collection("shadow_signals").get()
            fs_map = {doc.id: doc.to_dict().get('status') for doc in fs_signals}

            # 3. Detect Discrepancies
            missing_in_fs = [sid for sid in sql_map if sid not in fs_map]
            status_mismatch = [sid for sid in sql_map if sid in fs_map and sql_map[sid] != fs_map[sid]]

            return {
                "timestamp": datetime.datetime.utcnow(),
                "sql_count": len(sql_map),
                "firestore_count": len(fs_map),
                "missing_in_firestore": missing_in_fs,
                "status_mismatches": status_mismatch,
                "status": "PASS" if not missing_in_fs and not status_mismatch else "FAIL"
            }

    @staticmethod
    async def generate_reconciliation_report():
        audit = await ReconciliationService.run_shadow_reconciliation()
        report_path = "docs/nifty200/TRADEMIND_RECONCILIATION_REPORT.md"

        with open(report_path, "w") as f:
            f.write(f"# TRADEMIND AI: RECONCILIATION REPORT\n\n")
            f.write(f"**Audit Timestamp**: {audit['timestamp'].isoformat()} UTC\n")
            f.write(f"**Overall Status**: {audit['status']}\n\n")
            f.write(f"## Authoritative Summary\n")
            f.write(f"- Neon (SQL) Count: {audit['sql_count']}\n")
            f.write(f"- Firestore (Mirror) Count: {audit['firestore_count']}\n\n")

            if audit['missing_in_firestore']:
                f.write(f"### Missing in Firestore\n")
                for sid in audit['missing_in_firestore']:
                    f.write(f"- {sid}\n")

            if audit['status_mismatches']:
                f.write(f"### Status Mismatches\n")
                for sid in audit['status_mismatches']:
                    f.write(f"- {sid}\n")

        return report_path
