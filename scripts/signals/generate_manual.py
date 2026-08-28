import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def run_generation(symbols: list, asset_class: str = "EQUITY"):
    print(f"[*] Starting Manual Signal Generation for {len(symbols)} instruments ({asset_class})...")

    generated_count = 0
    rejected_count = 0

    for symbol in symbols:
        try:
            # P0 Quant Engine Integration
            signal = await SignalEngine.generate_signal(symbol, asset_class, "SWING")

            if signal:
                print(f"   [SIGNAL] {symbol}: {signal.rating} @ {signal.entry_price:.2f} (Prob: {signal.calibrated_probability:.2f})")
                await container.ios_repo.save_live_signal(signal)
                generated_count += 1
            else:
                rejected_count += 1

        except Exception as e:
            print(f"   [ERROR] Failed for {symbol}: {e}")

    print(f"\n[SUCCESS] Generation Complete.")
    print(f"   Total Generated: {generated_count}")
    print(f"   Total Rejected (No-Trade): {rejected_count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", choices=["NIFTY_200", "INDICES", "CUSTOM"], default="INDICES")
    parser.add_argument("--symbols", help="Comma-separated symbols for CUSTOM universe")
    parser.add_argument("--asset-class", default="EQUITY")

    args = parser.parse_args()

    symbols = []
    if args.universe == "NIFTY_200":
        symbols = NIFTY_200_CONSTITUENTS
    elif args.universe == "INDICES":
        symbols = ["NIFTY", "BANKNIFTY"]
    elif args.universe == "CUSTOM" and args.symbols:
        symbols = args.symbols.split(",")

    asyncio.run(run_generation(symbols, args.asset_class))
