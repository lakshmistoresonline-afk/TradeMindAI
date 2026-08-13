import os
import sys
import asyncio
import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container
from backend.services.stock_service import StockService
from backend.workers.tasks import _sync_stock_data_logic, _analyze_stock_ai_logic
from scripts.audit_database import ALL_SUPPORTED

async def populate_historical():
    print(f"--- STARTING HISTORICAL SIGNAL POPULATION ---")
    print(f"Targeting {len(ALL_SUPPORTED)} stocks...")

    for symbol in ALL_SUPPORTED:
        try:
            print(f"[*] Processing {symbol}...")
            # 1. Sync all historical data (10y to ensure we have the start)
            await _sync_stock_data_logic(symbol, period="10y")

            # 2. Run AI Analysis to generate signals
            # Note: _analyze_stock_ai_logic generates LiveSignal entries in Firestore/Postgres
            await _analyze_stock_ai_logic(symbol)

            print(f"[+] {symbol} Completed.")
        except Exception as e:
            print(f"[!] Error processing {symbol}: {e}")

        # Rate limiting / Sleep to avoid being blocked by APIs
        await asyncio.sleep(1)

    print("--- HISTORICAL POPULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(populate_historical())
