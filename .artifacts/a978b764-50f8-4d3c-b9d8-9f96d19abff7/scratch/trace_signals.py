import sys
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.signal_engine import SignalEngine

async def trace():
    print("============================================================")
    print(" SIGNAL ENGINE TRACE")
    print("============================================================")

    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN"]

    for s in symbols:
        print(f"[*] Generating signal for {s}...")
        sig = await SignalEngine.generate_signal(s, "EQUITY", "SWING")
        if sig:
            print(f"   [SIGNAL] {s}: {sig.rating} @ {sig.entry_price:.2f}")
            print(f"      Prob (Raw): {sig.raw_probability:.4f}")
            print(f"      Prob (Calib): {sig.calibrated_probability:.4f}")
            print(f"      EV: {sig.expected_value:.2f}R")
        else:
            print(f"   [NO_TRADE] {s}")

if __name__ == "__main__":
    asyncio.run(trace())
