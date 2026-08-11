import os
import sys
import asyncio
import uuid
import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container
from backend.domain.models.ios import ResearchNote

async def populate():
    print("[*] Seeding Research Notes...")
    try:
        notes = [
            {
                "symbol": "RELIANCE",
                "content": "Institutional accumulation phase observed at 2450-2500 levels. Order flow suggests significant DII support. AI bias is strongly positive for the monthly timeframe.",
                "tags": ["ACCUMULATION", "DII_SUPPORT"]
            },
            {
                "symbol": "TCS",
                "content": "Sector rotation favoring IT giants. Robust quarterly outlook and attractive PE relative to 5Y median. AI confirms bullish divergence in RSI.",
                "tags": ["IT_SECTOR", "BULLISH_DIVERGENCE"]
            }
        ]

        for n in notes:
            note = ResearchNote(
                id=str(uuid.uuid4()),
                user_id="SYSTEM_AI",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                **n
            )
            await container.ios_repo.save_research_note(note)
            print(f"   [+] Seeded Note: {n['symbol']}")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate())
