import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container

async def check():
    stocks = await container.repository.get_all_stocks(limit=50)
    for s in stocks:
        consensus = s.analysis.get("consensus", "") if s.analysis else "N/A"
        print(f"Symbol: {s.symbol:10} | Change%: {s.change_pct:6.2f} | AI Score: {s.ai_investment_score:6.2f} | Analysis: {bool(s.analysis)} | Consensus: {consensus[:20]}")

if __name__ == "__main__":
    asyncio.run(check())
