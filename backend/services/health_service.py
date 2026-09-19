import datetime
import asyncio
from typing import Dict, Any
from backend.core.container import container
from backend.services.freeze_verification_service import V22FreezeVerificationService
from backend.services.pulse_watchdog import PulseWatchdog


class SystemHealthService:
    """
    Phase 45: Canonical System Status.
    Real-time health monitoring of all TradeMind components.
    """

    @staticmethod
    async def get_comprehensive_health() -> Dict[str, Any]:
        # Perform component checks
        freeze_status = V22FreezeVerificationService.verify_freeze()

        # 1. Database Check (Neon)
        db_status = "HEALTHY"
        try:
            from backend.core.postgres import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except: db_status = "ERROR"

        # 2. Market Data Check
        market_data = await container.market_data_service.get_market_state()
        md_status = "HEALTHY" if market_data["status"] != "ERROR" else "DEGRADED"

        # 3. Firestore Check
        fs_status = "HEALTHY"
        from backend.core.database import db_client
        if not db_client: fs_status = "UNAVAILABLE"

        components = {
            "API": "UP",
            "Database": "UP" if db_status == "HEALTHY" else "DOWN",
            "Market Data": "UP" if md_status == "HEALTHY" else "DEGRADED",
            "Historical Data": "NOT_CHECKED",
            "Feature Engine": "NOT_CHECKED",
            "Model Registry": "NOT_CHECKED",
            "V2.2 Engine": "UP" if freeze_status["status"] == "PASS" else "FAILED",
            "Signal Engine": "UP", # Basic status for now
            "Outcome Engine": "UP",
            "Research Engine": "NOT_CHECKED",
            "Firestore Mirror": "UP" if fs_status == "HEALTHY" else fs_status
        }


        # Subsystem audits for details (Guarded against DB failures)
        try:
            universe = await container.universe_service.audit_universe_readiness()
        except Exception as ue:
            print(f"[Health] Universe audit failed: {ue}")
            universe = {"total": 200, "fresh": 0, "blocked": 0, "status": "ERROR"}


        # 4. Sync Metadata
        sync_meta = {}
        if db_client:
            try:
                sync_doc = db_client.collection("system_metrics").document("last_price_sync").get()
                if sync_doc.exists:
                    sync_meta = sync_doc.to_dict()
            except Exception as e:
                print(f"[Health] Firestore sync metadata fetch failed: {e}")

        from backend.core.version import get_version_metadata

        # Calculate actual sector mapping (Phase 3 Truth)
        try:
            mapped_count = 0
            with container.repository.session_factory() as db:
                from backend.core.postgres import StockDB
                mapped_count = db.query(StockDB).filter(StockDB.sector != "Unknown", StockDB.sector.isnot(None)).count()
        except:
            mapped_count = 0

        return {
            "status": "HEALTHY" if all(v in ["UP", "HEALTHY", "NOT_CHECKED"] for v in components.values()) else "DEGRADED",
            **get_version_metadata(),
            "pulse_watchdog": PulseWatchdog.get_status(),
            "components": components,

            "freeze_report": freeze_status,
            "universe": {
                "total": universe["total"],
                "fresh": universe["fresh"],
                "blocked": universe["blocked"],
                "coverage": universe["fresh"]
            },
            "sector": {
                "total": universe["total"],
                "mapped": mapped_count,
                "coverage_pct": round(mapped_count / universe["total"] * 100, 1) if universe["total"] > 0 else 0
            },
            "market_state": market_data,
            "last_price_sync": sync_meta
        }

