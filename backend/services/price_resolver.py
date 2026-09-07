import datetime
import pandas as pd
from typing import Dict, Any, Optional, List
from backend.core.container import container
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

class ProviderCapabilityRegistry:
    @staticmethod
    def get_capabilities(provider_name: str) -> Dict[str, Any]:
        """
        Defines what each provider can safely support.
        """
        registry = {
            "UpstoxProvider": {
                "equity_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE"]
            },
            "DhanProvider": {
                "equity_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE"]
            },
            "GrowwProvider": {
                "equity_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE", "BSE"]
            },
            "YFinanceProvider": {
                "equity_support": True,
                "index_support": True,
                "future_support": False,
                "option_support": False,
                "exchanges": ["NSE", "BSE"]
            }
        }
        return registry.get(provider_name, {
            "equity_support": True,
            "future_support": False,
            "option_support": False,
            "exchanges": ["NSE"]
        })

class PriceResolver:
    """
    Workstream 15: Institutional Multi-Provider Price Resolver.
    Implements deterministic failover: Upstox -> Dhan -> Groww -> YFinance.
    Enforces strict F&O-only routing for derivative premiums.
    """

    EQUITY_SEQUENCE = ["upstox", "dhan", "groww", "yfinance"]
    FNO_SEQUENCE = ["upstox", "dhan", "groww"] # YFinance FORBIDDEN for F&O

    @classmethod
    async def resolve_current_price(cls, signal: LiveSignal) -> Dict[str, Any]:
        """
        Entry point for institutional price resolution.
        """
        asset_class = signal.asset_class

        # 1. Select Sequence
        if asset_class in ["FUTURES", "OPTIONS"]:
             sequence = cls.FNO_SEQUENCE
        else:
             sequence = cls.EQUITY_SEQUENCE

        # 2. Re-prioritize based on settings
        primary = settings.MARKET_DATA_PROVIDER
        if primary in sequence:
            sequence = [primary] + [p for p in sequence if p != primary]

        # 3. Iterate through providers
        for provider_code in sequence:
            res = await cls._try_resolve_with_provider(signal, provider_code)
            if res["status"] == "FRESH":
                return res

        # 4. Final Fallback (NULL)
        return {
            "current_price": None,
            "underlying_price": None,
            "normalized_current_price": None,
            "timestamp": datetime.datetime.now(),
            "source": "FAILOVER_EXHAUSTED",
            "status": "DATA_UNAVAILABLE",
            "eligibility": "DATA_BLOCKED"
        }

    @staticmethod
    async def _try_resolve_with_provider(signal: LiveSignal, provider_code: str) -> Dict[str, Any]:
        # Local instantiation to avoid container pollution during failover
        from backend.infrastructure.repositories.upstox_provider import UpstoxProvider
        from backend.infrastructure.repositories.dhan_provider import DhanProvider
        from backend.infrastructure.repositories.groww_provider import GrowwProvider
        from backend.infrastructure.repositories.yfinance_provider import YFinanceProvider

        providers = {
            "upstox": UpstoxProvider,
            "dhan": DhanProvider,
            "groww": GrowwProvider,
            "yfinance": YFinanceProvider
        }

        provider_cls = providers.get(provider_code)
        if not provider_cls:
             return {"status": "PROVIDER_NOT_FOUND"}

        provider = provider_cls()
        provider_name = provider.__class__.__name__
        caps = ProviderCapabilityRegistry.get_capabilities(provider_name)

        # Capability check
        asset_class = signal.asset_class
        supported = True
        if asset_class == "FUTURES" and not caps.get("future_support"): supported = False
        if asset_class == "OPTIONS" and not caps.get("option_support"): supported = False

        if not supported:
            return {"status": "PROVIDER_UNSUPPORTED"}

        # Resolve
        instr_id = signal.instrument_id or signal.symbol
        now = datetime.datetime.now()

        try:
            # Fetch LTP
            u_sym = signal.underlying_symbol or signal.symbol
            u_price = await provider.get_ltp(u_sym)

            if asset_class in ["EQUITY", "INDEX"]:
                price = u_price
            else:
                price = await provider.get_ltp(instr_id)
                # Anti-Contamination Check (Underlying != Derivative)
                if u_price and price and abs(price - u_price) < 0.0001:
                    return {"status": "IDENTITY_MISMATCH", "reason": "Derivative premium equals underlying spot."}

            if price and price > 0:
                return {
                    "current_price": price,
                    "underlying_price": u_price,
                    "timestamp": now,
                    "source": provider_name,
                    "status": "FRESH"
                }
        except Exception as e:
            print(f"   [!] Failover: {provider_name} failed for {signal.symbol}: {e}")

        return {"status": "PROVIDER_ERROR"}
