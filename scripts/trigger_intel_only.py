import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

from backend.workers.tasks import _process_intel_logic
from backend.core.postgres import init_db

async def trigger():
    print("--- TradeMind AI: TRIGGERING MARKET INTELLIGENCE ONLY ---")
    init_db()
    await _process_intel_logic()
    print("--- TRIGGER COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(trigger())
