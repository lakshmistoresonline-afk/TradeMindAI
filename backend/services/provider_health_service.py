import datetime
import asyncio
from typing import Dict, Any, List
from backend.core.container import container
from backend.core.config import settings

class ProviderHealthService:
    """
    Workstream 21: Market Data Provider Health Monitor.
    Tracks authentication, latency, and capability across all configured providers.
    """

    @staticmethod
    async def get_provider_health() -> Dict[str, Any]:
        from backend.infrastructure.repositories.upstox_provider import UpstoxProvider
        from backend.infrastructure.repositories.dhan_provider import DhanProvider
        from backend.infrastructure.repositories.yfinance_provider import YFinanceProvider

        providers = {
            "UPSTOX": UpstoxProvider(),
            "DHAN": DhanProvider(),
            "YFINANCE": YFinanceProvider()
        }

        health = {}
        for name, p in providers.items():
            start = datetime.datetime.now()
            try:
                # Test connectivity with a stable symbol
                ltp = await p.get_ltp("RELIANCE")
                latency = (datetime.datetime.now() - start).total_seconds()

                health[name] = {
                    "status": "HEALTHY" if ltp > 0 else "DEGRADED",
                    "latency": f"{latency:.3f}s",
                    "auth": "PASS" if ltp > 0 else "REQUIRED",
                    "last_check": datetime.datetime.now().isoformat()
                }
            except Exception as e:
                health[name] = {
                    "status": "OFFLINE",
                    "error": str(e),
                    "last_check": datetime.datetime.now().isoformat()
                }

        return health
