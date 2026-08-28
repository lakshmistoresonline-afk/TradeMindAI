import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.api.v1.endpoints.analysis import get_performance_summary, get_performance_signals

async def test():
    print("--- TESTING PERFORMANCE SUMMARY API ---")
    res = await get_performance_summary()
    print(f"[*] Keys: {res.keys()}")
    print(f"[*] Range: {res['range']}")
    print(f"[*] Evolution Labels: {res['evolution']['labels']}")
    print(f"[*] Live Signals Total: {res['live_signals']['total']}")
    print(f"[*] Backtest Signals Total: {res['backtest_signals']['total']}")

    print("\n--- TESTING PERFORMANCE SIGNALS API ---")
    sigs = await get_performance_signals()
    print(f"[*] Total Signals Returned: {len(sigs)}")
    if sigs:
        print(f"[*] Sample Signal: {sigs[0]['symbol']} ({sigs[0]['dataset']}) @ {sigs[0].get('timestamp') or sigs[0].get('date')}")

if __name__ == "__main__":
    asyncio.run(test())
