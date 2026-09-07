import datetime
import pandas as pd
from typing import Dict, Any, Optional
from backend.core.container import container
from backend.domain.models.ios import LiveSignal

class ProviderCapabilityRegistry:
    @staticmethod
    def get_capabilities(provider_name: str) -> Dict[str, Any]:
        """
        Part 6: Provider Capability Registry.
        Defines what each provider can safely support.
        """
        registry = {
            "GrowwProvider": {
                "equity_support": True,
                "index_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE", "BSE"]
            },
            "YFinanceProvider": {
                "equity_support": True,
                "index_support": True,
                "future_support": False, # Yahoo NSE futures are unreliable
                "option_support": False, # Options coverage is poor
                "exchanges": ["NSE", "BSE"]
            },
            "UpstoxProvider": {
                "equity_support": True,
                "index_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE"]
            },
            "DhanProvider": {
                "equity_support": True,
                "index_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE"]
            },
            "UpstoxProvider": {
                "equity_support": True,
                "index_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE"]
            },
            "DhanProvider": {
                "equity_support": True,
                "index_support": True,
                "future_support": True,
                "option_support": True,
                "exchanges": ["NSE"]
            }
        }
        return registry.get(provider_name, {
            "equity_support": True,
            "index_support": True,
            "future_support": False,
            "option_support": False,
            "exchanges": ["NSE"]
        })

class PriceResolver:
    @staticmethod
    async def resolve_current_price(signal: LiveSignal) -> Dict[str, Any]:
        """
        Step 2E Canonical Price Resolver.
        Implements:
        - Instrument eligibility
        - Provider capability check
        - Expiry validation
        - Zero-fabrication defense
        - Separate underlying/instrument price
        """
        provider = container.provider
        provider_name = provider.__class__.__name__
        caps = ProviderCapabilityRegistry.get_capabilities(provider_name)

        asset_class = signal.asset_class
        symbol = signal.symbol
        instr_id = signal.instrument_id or symbol

        now = datetime.datetime.now()

        # P0 Rule: Initialize with NULLs (Part 5)
        result = {
            "current_price": None,
            "underlying_price": None,
            "normalized_current_price": None,
            "timestamp": now,
            "source": provider_name,
            "status": "DATA_UNAVAILABLE",
            "eligibility": "ELIGIBLE"
        }

        # 1. Expiry Validation (Part 9)
        if signal.expiry:
            expiry_dt = signal.expiry
            if isinstance(expiry_dt, str):
                try:
                    expiry_dt = datetime.datetime.fromisoformat(expiry_dt)
                except:
                    expiry_dt = None

            # Use UTC comparison if expiry is UTC, otherwise local
            if expiry_dt and expiry_dt.replace(tzinfo=None) < now.replace(tzinfo=None):
                result["status"] = "EXPIRED"
                result["eligibility"] = "EXPIRED_INSTRUMENT"
                return result

        try:
            # 2. Provider Support Check (Part 6)
            supported = True
            if asset_class == "FUTURES" and not caps.get("future_support"): supported = False
            if asset_class == "OPTIONS" and not caps.get("option_support"): supported = False

            if not supported:
                result["status"] = "PROVIDER_UNSUPPORTED"
                result["eligibility"] = "INSTRUMENT_BLOCKED"
                return result

            # 3. Fetch Underlying Price (Spot/Index)
            u_sym = signal.underlying_symbol or symbol
            u_price = await provider.get_ltp(u_sym)

            # Part 4 & 7: Zero Price Defense
            if u_price and u_price > 0:
                result["underlying_price"] = u_price
            else:
                result["underlying_price"] = None

            # 4. Fetch Instrument Price
            if asset_class == "EQUITY" or asset_class == "INDEX":
                result["current_price"] = result["underlying_price"]
                result["status"] = "FRESH" if result["current_price"] else "DATA_UNAVAILABLE"
                if not result["current_price"]:
                    result["eligibility"] = "DATA_BLOCKED"

            elif asset_class in ["FUTURES", "OPTIONS"]:
                # Part 10 & 11: Absolute separation
                d_price = await provider.get_ltp(instr_id)

                if d_price and d_price > 0:
                    # Part 4: Underlying Contamination Check
                    if result["underlying_price"] and abs(d_price - result["underlying_price"]) < 0.0001:
                        # Hard Contamination Check
                        result["current_price"] = None
                        result["status"] = "INVALID"
                        result["eligibility"] = "INVALID_DATA"
                    else:
                        result["current_price"] = d_price
                        result["status"] = "FRESH"
                else:
                    result["current_price"] = None
                    result["status"] = "INSTRUMENT_NOT_FOUND"
                    result["eligibility"] = "DATA_BLOCKED"

            # 5. Apply Normalization (Part 17)
            factor = getattr(signal, 'price_adjustment_factor', 1.0)
            if factor is None: factor = 1.0

            if result["current_price"]:
                result["normalized_current_price"] = result["current_price"] * factor
            else:
                result["normalized_current_price"] = None

        except Exception as e:
            print(f"[PriceResolver] Error resolving {symbol}: {e}")
            result["status"] = "ERROR"
            result["eligibility"] = "DATA_BLOCKED"

        return result
