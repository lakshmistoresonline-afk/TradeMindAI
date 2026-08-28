import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def main():
    print("[*] Finalizing Step 2A Forensics...")
    sigs = await container.ios_repo.get_active_live_signals()
    print(f"REPO_SIGNALS_COUNT: {len(sigs)}")

    master_sigs = [s for s in sigs if s.id.startswith('master_')]
    print(f"MASTER_SIGNALS_COUNT: {len(master_sigs)}")

    if master_sigs:
        s = master_sigs[0]
        print(f"Sample Signal: {s.symbol} | Entry: {s.entry_price} | Prob: {s.calibrated_probability}")

if __name__ == "__main__":
    asyncio.run(main())
