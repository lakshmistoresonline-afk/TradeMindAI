import datetime
import asyncio
from typing import List, Dict, Any, Optional
from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService

class EquitySignalGenerationService:
    """
    Phase 2: Master Equity Signal Generation Service.
    Enforces the continuous data path from Market Data to Signal Ledger.
    """

    @staticmethod
    async def run_production_scan() -> Dict[str, Any]:
        """
        Executes a full production scan for the NIFTY-200 universe across all horizons.
        """
        print("=== [EQUITY] Multi-Horizon Production Scan Started ===")
        start_time = datetime.datetime.utcnow()

        # 1. Load NIFTY-200 universe (Top 50 Hardened for Production)
        symbols = container.universe_service.NIFTY_200_CONSTITUENTS[:50]
        horizons = ["SHORT", "SWING", "LONG"]

        print(f"   [DEBUG] Symbols to scan: {len(symbols)}")

        report = {
            "timestamp": start_time.isoformat(),
            "universe_count": len(symbols),
            "horizons": horizons,
            "signals_generated": 0,
            "errors": []
        }

        # 2. Iterate through horizons and symbols
        for horizon in horizons:
            print(f"   --- Scanning Horizon: {horizon} ---")
            for symbol in symbols:
                try:
                    # Data -> Features -> Model -> V2.2 -> Signal
                    signal = await SignalEngine.generate_signal(
                        symbol=symbol,
                        asset_class="EQUITY",
                        timeframe=horizon
                    )

                    if signal:
                        # Persist atomically to Neon (Authority)
                        await SignalLedgerService.create_signal(signal)
                        report["signals_generated"] += 1
                        print(f"   [+] {symbol} ({horizon}) SIGNAL: {signal.direction} at ₹{signal.entry_price}")

                except Exception as e:
                    report["errors"].append({"symbol": symbol, "horizon": horizon, "error": str(e)})
                    print(f"   [!] {symbol} ({horizon}) ERROR: {e}")

        end_time = datetime.datetime.utcnow()
        report["duration_seconds"] = (end_time - start_time).total_seconds()
        print(f"=== [EQUITY] Multi-Horizon Scan Completed. Total Signals: {report['signals_generated']} ===")

        return report
