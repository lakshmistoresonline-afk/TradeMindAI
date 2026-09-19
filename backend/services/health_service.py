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
        """
        Hardened Evidence-Driven Health Monitor (Phase 4).
        No synthetic data. All statuses derived from component probes.
        """
        # 1. Dependency Probes
        freeze_status = V22FreezeVerificationService.verify_freeze()

        # 1.1 Database (SQL Authority)
        sql_health = "FAILED"
        try:
            from backend.core.postgres import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                sql_health = "HEALTHY"
        except: pass

        # 1.2 Cache (Redis)
        redis_health = "FAILED"
        try:
            from redis import asyncio as aioredis
            from backend.core.config import settings
            r = aioredis.from_url(settings.REDIS_URL, socket_timeout=1)
            if await r.ping(): redis_health = "HEALTHY"
            await r.close()
        except: pass

        # 1.3 Market Data & Freshness
        market_data = await container.market_data_service.get_market_state()
        md_status = market_data.get("status", "UNAVAILABLE")
        freshness = market_data.get("freshness", "UNAVAILABLE")

        # 1.4 Signal Ledger (Integrity check)
        ledger_health = "NOT_CHECKED"
        try:
             with container.repository.session_factory() as db:
                 from backend.core.postgres import LiveSignalDB
                 # Basic availability check
                 db.query(LiveSignalDB).limit(1).all()
                 ledger_health = "HEALTHY"
        except: ledger_health = "FAILED"

        # 2. Components Aggregation
        components = {
            "API": "HEALTHY",
            "SQL_Database": sql_health,
            "Redis_Cache": redis_health,
            "Market_Feed": md_status,
            "V2.2_Engine": "HEALTHY" if freeze_status["status"] == "PASS" else "FAILED",
            "Signal_Ledger": ledger_health,
            "Pulse_Watchdog": PulseWatchdog.get_status().get("status", "UNKNOWN")
        }

        # 3. Overall Determination
        critical = ["SQL_Database", "Redis_Cache", "Signal_Ledger"]
        status = "HEALTHY"
        if any(components[c] == "FAILED" for c in critical): status = "FAILED"
        elif any(v != "HEALTHY" for v in components.values()): status = "DEGRADED"

        # 4. Sync Metadata (Observability)
        from backend.core.database import db_client
        sync_meta = {}
        if db_client:
            try:
                sync_doc = db_client.collection("system_metrics").document("last_price_sync").get()
                if sync_doc.exists: sync_meta = sync_doc.to_dict()
            except: pass

        from backend.core.version import get_version_metadata

        return {
            "status": status,
            **get_version_metadata(),
            "pulse": PulseWatchdog.get_status(),
            "components": components,
            "market": {
                "regime": market_data.get("regime"),
                "vix": market_data.get("vix"),
                "freshness": freshness,
                "observation_timestamp": market_data.get("observation_timestamp")
            },
            "last_sync": sync_meta,
            "probed_at": datetime.datetime.now(timezone.utc).isoformat()
        }

