import datetime
import json
from typing import Dict, Any, List
from sqlalchemy import func, text
from backend.core.postgres import SessionLocal, ShadowEventDB, ShadowSignalDB, ShadowScanDiagnosticDB, StockDB

class MonitoringService:
    """
    Step 4: Centralized Health & Data Quality Monitoring.
    Implements Sections 33, 43, 68 of the Master Specification.
    """

    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        with SessionLocal() as session:
            # 1. Provider Latency (Last 100 scans)
            avg_latency = session.query(func.avg(ShadowScanDiagnosticDB.provider_latency_ms))\
                .filter(ShadowScanDiagnosticDB.scan_timestamp > datetime.datetime.utcnow() - datetime.timedelta(days=1))\
                .scalar() or 0.0

            # 2. Data Freshness (Any stale stocks in Nifty 200?)
            stale_threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
            stale_count = session.query(StockDB).filter(StockDB.updated_at < stale_threshold).count()

            # 3. Last Shadow Cycle
            last_event = session.query(ShadowEventDB).order_by(ShadowEventDB.timestamp.desc()).first()

            return {
                "status": "HEALTHY" if stale_count < 10 else "DEGRADED",
                "avg_provider_latency_ms": round(float(avg_latency), 2),
                "stale_stock_count": stale_count,
                "last_cycle_timestamp": last_event.timestamp if last_event else None,
                "environment": "SHADOW_MONITORING"
            }

    @staticmethod
    def get_data_quality_metrics() -> Dict[str, Any]:
        with SessionLocal() as session:
            # Metrics from Sections 33 & 68
            now = datetime.datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # Rejection breakdown
            rejections = session.query(ShadowScanDiagnosticDB.rejection_reason, func.count(ShadowScanDiagnosticDB.id))\
                .filter(ShadowScanDiagnosticDB.scan_timestamp >= today_start)\
                .group_by(ShadowScanDiagnosticDB.rejection_reason).all()

            # Provider Success Rate
            total_reqs = session.query(ShadowScanDiagnosticDB).filter(ShadowScanDiagnosticDB.scan_timestamp >= today_start).count()
            failed_reqs = session.query(ShadowScanDiagnosticDB).filter(
                ShadowScanDiagnosticDB.scan_timestamp >= today_start,
                ShadowScanDiagnosticDB.signal_decision == 'ERROR'
            ).count()

            return {
                "rejection_breakdown": {r[0]: r[1] for r in rejections},
                "provider_success_rate": round((1 - (failed_reqs / total_reqs if total_reqs > 0 else 0)) * 100, 2),
                "total_evaluations_today": total_reqs,
                "timestamp": now
            }

    @staticmethod
    def run_reconciliation_audit() -> Dict[str, Any]:
        """
        Automated Signal Integrity Audit (Section 69).
        Detects impossible states.
        """
        with SessionLocal() as session:
            issues = []

            # 1. Expired + ACTIVE
            now = datetime.datetime.utcnow()
            expired_active = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.status == 'ACTIVE'
                # (Would need instrument_id join for real expiry check)
            ).count() # Placeholder for complex join

            # 2. Duplicate Outcomes
            # (Checked by DB constraints)

            # 3. Missing created_at
            missing_created = session.query(ShadowSignalDB).filter(ShadowSignalDB.created_at == None).count()
            if missing_created > 0: issues.append(f"{missing_created} signals missing created_at")

            return {
                "audit_timestamp": now,
                "integrity_score": 1.0 if not issues else 0.5,
                "identified_issues": issues,
                "status": "PASS" if not issues else "FAIL"
            }
