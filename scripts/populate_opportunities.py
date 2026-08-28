import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container

async def populate():
    print("[*] Populating Opportunities...")
    try:
        stocks = await container.repository.get_all_stocks(limit=100)
        if not stocks:
            print("[!] No stocks found in database to scan for opportunities.")
            return

        opportunities = container.opportunity_engine.find_opportunities(stocks)
        print(f"[*] Found {len(opportunities)} opportunities.")

        for opp in opportunities:
            await container.ios_repo.save_opportunity(opp)
            print(f"   [+] Saved: {opp.symbol} ({opp.type})")

        print("[*] Opportunities population complete.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate())
