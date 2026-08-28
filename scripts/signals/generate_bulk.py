import os
import sys
import asyncio
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def generate(universe: str):
    print(f"[*] Starting Bulk Signal Generation for universe: {universe}")

    symbols = []
    if universe == "NIFTY_200":
        symbols = NIFTY_200_CONSTITUENTS

    for symbol in symbols:
        print(f"   [*] Processing {symbol}...")
        try:
            # Try to generate signal for 1D timeframe
            signal = await SignalEngine.generate_signal(symbol, "EQUITY", "SWING")
            if signal:
                print(f"      [SIGNAL] {symbol}: {signal.direction} @ {signal.entry_price:.2f} (Conviction: {signal.conviction:.1f}%)")
                await container.ios_repo.save_live_signal(signal)
            else:
                print(f"      [INFO] No high-conviction signal found for {symbol}.")

        except Exception as e:
            print(f"      [ERROR] {symbol}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", choices=["NIFTY_200"], default="NIFTY_200")
    args = parser.parse_args()

    asyncio.run(generate(args.universe))
