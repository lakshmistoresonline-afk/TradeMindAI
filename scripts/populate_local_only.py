import os
import sys
import asyncio
import json
import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. FORCE LOCAL SQLITE
os.environ["POSTGRES_URL"] = "sqlite:///./local_operational.db"
os.environ["USE_LOCAL_LLM"] = "True"

# Load environment (will be overridden by env vars above)
load_dotenv(os.path.join("backend", ".env"))

from backend.core.postgres import SessionLocal, init_db
from backend.core.container import container
from scripts.audit_database import ALL_SUPPORTED
from backend.workers.tasks import _sync_stock_data_logic, _analyze_stock_ai_logic

async def populate_local():
    print("--- TRADEMIND AI: OFFLINE LOCAL POPULATION ENGINE ---")
    print(f"Target Database: {os.environ['POSTGRES_URL']}")

    # Ensure local DB schema is up to date
    init_db()

    for symbol in ALL_SUPPORTED:
        print(f"[*] Local Processing: {symbol}...")
        try:
            # Sync Technicals
            await _sync_stock_data_logic(symbol, period="1y")
            # Run Local AI
            result = await _analyze_stock_ai_logic(symbol)
            print(f"   [+] Result: {result}")
        except Exception as e:
            print(f"   [!] Error: {e}")

        await asyncio.sleep(0.1)

    print("--- LOCAL POPULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(populate_local())
