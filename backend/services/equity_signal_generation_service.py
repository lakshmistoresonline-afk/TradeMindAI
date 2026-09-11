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
        Executes a full production scan for the NIFTY-200 universe.
        """
        print("=== [EQUITY] Production Scan Started ===")
        start_time = datetime.datetime.utcnow()

        # 1. Load NIFTY-200 universe
        symbols = container.universe_service.NIFTY_200_CONSTITUENTS

        report = {
            "timestamp": start_time.isoformat(),
            "universe_count": len(symbols),
            "signals_generated": 0,
            "errors": []
        }

        # 2. Iterate through universe
        for symbol in symbols:
            try:
                # 3-17. Data -> Features -> Model -> V2.2 -> Signal (Encapsulated in SignalEngine)
                signal = await SignalEngine.generate_signal(
                    symbol=symbol,
                    asset_class="EQUITY",
                    timeframe="SWING"
                )

                if signal:
                    # 18. Persist atomically to Neon (Authority)
                    # 21. Mirror to Firestore (Managed inside SignalLedgerService)
                    await SignalLedgerService.create_signal(signal)
                    report["signals_generated"] += 1
                    print(f"   [+] {symbol} SIGNAL: {signal.direction} at ₹{signal.entry_price}")

            except Exception as e:
                report["errors"].append({"symbol": symbol, "error": str(e)})
                print(f"   [!] {symbol} ERROR: {e}")

        end_time = datetime.datetime.utcnow()
        report["duration_seconds"] = (end_time - start_time).total_seconds()
        print(f"=== [EQUITY] Production Scan Completed. Signals: {report['signals_generated']} ===")

        return report
