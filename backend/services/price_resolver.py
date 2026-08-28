import datetime
import pandas as pd
import yfinance as yf
from typing import Dict, Any, Optional
from backend.core.container import container
from backend.domain.models.ios import LiveSignal

class PriceResolver:
    @staticmethod
    async def resolve_current_price(signal: LiveSignal) -> Dict[str, Any]:
        """
        Canonical Price Resolver (Step 2D).
        Resolves current_price, underlying_price, and applies normalization.
        """
        provider = container.provider
        asset_class = signal.asset_class
        symbol = signal.symbol
        instr_id = signal.instrument_id or symbol

        # P0 Rule: Initialize with NULLs, not 0.0 (Part 8/26)
        result = {
            "current_price": None,
            "underlying_price": None,
            "normalized_current_price": None,
            "timestamp": datetime.datetime.now(),
            "source": provider.__class__.__name__,
            "status": "DATA_UNAVAILABLE"
        }

        try:
            # 1. Fetch Underlying Price (Spot/Index)
            u_sym = signal.underlying_symbol or symbol
            u_price = await provider.get_ltp(u_sym)

            # Part 7: Zero Price Rule
            if u_price > 0:
                result["underlying_price"] = u_price
            else:
                result["underlying_price"] = None

            # 2. Fetch Instrument Price
            if asset_class == "EQUITY" or asset_class == "INDEX":
                result["current_price"] = result["underlying_price"]
                result["status"] = "FRESH" if result["current_price"] else "DATA_UNAVAILABLE"

            elif asset_class == "FUTURES":
                # For Futures, use instr_id (e.g. RELIANCE26AUGFUT.NS)
                f_price = await provider.get_ltp(instr_id)

                # Part 7 & 10: Ensure futures price is valid and separate from spot
                if f_price > 0:
                    # Basic mapping defense: spot usually != future (Part 10)
                    if result["underlying_price"] and abs(f_price - result["underlying_price"]) < 0.01:
                         # Highly unlikely for NSE futures to be EXACTLY spot unless mapping failed
                         # but for Nifty it might be very close. We tag it.
                         result["current_price"] = f_price
                         result["status"] = "FRESH_SPOT_ALIGNED"
                    else:
                         result["current_price"] = f_price
                         result["status"] = "FRESH"
                else:
                    result["current_price"] = None
                    result["status"] = "INSTRUMENT_NOT_FOUND"

            elif asset_class == "OPTIONS":
                # Defect 1 Fix: Fetch actual premium from specific ticker
                # Part 8: Never fallback to underlying
                o_price = await provider.get_ltp(instr_id)

                if o_price > 0:
                    if result["underlying_price"] and o_price == result["underlying_price"]:
                        # Hard Contamination Check (Defect 1)
                        result["current_price"] = None
                        result["status"] = "DERIVATIVE_MAPPING_FAILURE"
                    else:
                        result["current_price"] = o_price
                        result["status"] = "FRESH"
                else:
                    result["current_price"] = None
                    result["status"] = "DERIVATIVE_DATA_UNAVAILABLE"

            # 3. Apply Normalization Factor (Step 2D - Part 19)
            factor = getattr(signal, "price_adjustment_factor", 1.0)
            if result["current_price"]:
                result["normalized_current_price"] = result["current_price"] * factor
            else:
                result["normalized_current_price"] = None

        except Exception as e:
            print(f"[PriceResolver] Error resolving {symbol}: {e}")
            result["status"] = "ERROR"

        return result
