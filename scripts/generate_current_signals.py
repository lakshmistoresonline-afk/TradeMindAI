import asyncio
import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService

async def main():
    print("=== TRADEMIND AI: CURRENT SIGNAL GENERATION ===")

    # 1. Fetch Universe
    symbols = ["COALINDIA", "NTPC", "YESBANK", "AXISBANK", "DALBHARAT", "ADANIENT", "ZYDUSLIFE", "UCOBANK", "BPCL", "INFY"]

    count = 0
    for symbol in symbols:
        try:
            print(f"Evaluating {symbol}...")
            signal = await SignalEngine.generate_signal(
                symbol=symbol,
                asset_class="EQUITY",
                timeframe="SWING"
            )

            if signal:
                print(f"   [+] SIGNAL GENERATED: {symbol} {signal.direction} at ₹{signal.entry_price}")
                await SignalLedgerService.create_signal(signal)
                count += 1
        except Exception as e:
            print(f"   [!] Error evaluating {symbol}: {e}")

    print(f"\nDone. {count} signals generated.")

if __name__ == "__main__":
    asyncio.run(main())
