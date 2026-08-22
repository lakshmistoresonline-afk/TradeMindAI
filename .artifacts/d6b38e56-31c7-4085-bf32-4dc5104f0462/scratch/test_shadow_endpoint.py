import os
import sys
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.api.v1.endpoints.shadow import get_shadow_status, get_shadow_summary, get_active_signals

async def test():
    print("Testing Shadow Endpoints...")
    try:
        status = await get_shadow_status()
        print(f"Status: {status}")

        summary = await get_shadow_summary()
        print(f"Summary: {summary}")

        active = await get_active_signals()
        print(f"Active Signals Count: {len(active)}")
        for a in active:
            print(f"  - {a['symbol']} ({a['status']})")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
