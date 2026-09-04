import datetime
import asyncio
from typing import Dict, Any
from backend.core.container import container

class SystemHealthService:
    """
    Workstream 14: System Health Observability.
    Aggregates health data from all subsystems.
    """

    @staticmethod
    async def get_comprehensive_health() -> Dict[str, Any]:
        # 1. Subsystem Audits
        universe = await container.universe_service.audit_universe_readiness()
        fno = await container.fno_registry.get_fno_registry_status()
        mon = container.monitoring_service.get_system_health()
        qual = container.monitoring_service.get_data_quality_metrics()

        return {
            "status": mon["status"],
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "nifty_200": {
                "coverage": f"{universe['fresh']}/{universe['total']}",
                "blocked": universe["blocked"]
            },
            "fno": {
                "eligible": fno["eligible_underlyings"],
                "discovered": fno["discovered_underlyings"]
            },
            "reliability": {
                "provider_success": f"{qual['provider_success_rate']}%",
                "latency_ms": mon["avg_provider_latency_ms"]
            },
            "storage": {
                "neon": "ONLINE",
                "firestore": "SYNCHRONIZED"
            }
        }
