import datetime
from typing import Dict, Any, List
from backend.core.postgres import SessionLocal, ShadowSignalDB, StockDB

class DataQualityService:
    """
    Workstream 28: Daily Data Integrity Report.
    Audits the entire signal ledger for completeness and anomalies.
    """

    @staticmethod
    def generate_integrity_report() -> Dict[str, Any]:
        with SessionLocal() as session:
            total = session.query(ShadowSignalDB).count()

            # Population Breakdown (Workstream 6/17)
            verified = session.query(ShadowSignalDB).filter(ShadowSignalDB.evaluation_mode == 'LIVE_SHADOW_VERIFIED').count()
            active = session.query(ShadowSignalDB).filter(ShadowSignalDB.evaluation_mode == 'LIVE_SHADOW_ACTIVE').count()
            reconstructed = session.query(ShadowSignalDB).filter(ShadowSignalDB.evaluation_mode == 'HISTORICAL_RECONSTRUCTED').count()
            legacy = session.query(ShadowSignalDB).filter(ShadowSignalDB.evaluation_mode == 'LEGACY_UNVERIFIED').count()

            # Anomalies
            missing_prediction = session.query(ShadowSignalDB).filter(ShadowSignalDB.prediction_id == None).count()
            missing_provenance = session.query(ShadowSignalDB).filter(ShadowSignalDB.provenance_id == None).count()

            # Look-ahead check (Authoritative)
            lookahead_violations = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.data_timestamp > ShadowSignalDB.timestamp
            ).count()

            # Data Freshness
            stale_stocks = session.query(StockDB).filter(
                StockDB.updated_at < datetime.datetime.utcnow() - datetime.timedelta(hours=24)
            ).count()

            return {
                "report_timestamp": datetime.datetime.utcnow().isoformat(),
                "population": {
                    "total_signals": total,
                    "verified_outcomes": verified,
                    "active_signals": active,
                    "unverified_historical": total - verified - active
                },
                "integrity_metrics": {
                    "prediction_linkage_pct": round((total - missing_prediction) / total * 100, 2) if total > 0 else 0.0,
                    "provenance_coverage_pct": round((total - missing_provenance) / total * 100, 2) if total > 0 else 0.0,
                    "lookahead_violation_count": lookahead_violations,
                    "stale_data_stock_count": stale_stocks
                },
                "status": "PASS" if lookahead_violations == 0 and stale_stocks < 10 else "WARNING"
            }
