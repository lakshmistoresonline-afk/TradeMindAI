import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def audit():
    print(f"Total NIFTY 200 Constituents: {len(NIFTY_200_CONSTITUENTS)}")

    unavailable = ["GUJGASLTD", "LTIM"] # As per prompt
    operational = [s for s in NIFTY_200_CONSTITUENTS if s not in unavailable]

    print(f"Operational: {len(operational)}")
    print(f"Unavailable: {len(unavailable)} ({', '.join(unavailable)})")

    if len(NIFTY_200_CONSTITUENTS) == 200:
        print("Universe Integrity: PASS")
    else:
        print("Universe Integrity: FAIL (Expected 200)")

if __name__ == "__main__":
    asyncio.run(audit())
