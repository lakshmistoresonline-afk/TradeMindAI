import asyncio
import datetime
import sys
import os

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.core.container import container
from backend.services.signal_engine import SignalEngine

async def test_signal():
    symbol = "ADANIENT"
    print(f"=== Testing Signal Generation for {symbol} ===")

    # 1. Fetch champ
    champ = await container.data_platform_repo.get_champion_model(symbol, horizon="LONG")
    if not champ:
        print(f"   [!] No champ for {symbol} SWING")
        return

    print(f"   Champion: {champ.name}, AUC={champ.roc_auc}")

    # 2. Generate
    signal = await SignalEngine.generate_signal(
        symbol=symbol,
        asset_class="EQUITY",
        timeframe="LONG"
    )

    if signal:
        print(f"   [SUCCESS] Signal: {signal.direction} at ₹{signal.entry_price}")
        print(f"   Quality: {signal.quality_class}")
    else:
        print(f"   [FAILED] No signal generated.")

if __name__ == "__main__":
    asyncio.run(test_signal())
