import asyncio
import os
import sys
import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

from backend.core.container import container
from backend.workers.tasks import _analyze_stock_logic, _process_intel_logic
from backend.core.postgres import init_db

async def populate():
    print("--- TradeMind AI: PRODUCTION DATA POPULATION SPRINT (RC-4) ---")

    # Initialize DB (Cloud Postgres)
    init_db()

    # Target core symbols first
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    print(f"Ingesting {len(symbols)} high-conviction symbols...")

    for symbol in symbols:
        try:
            print(f"Analyzing {symbol}...")
            # Use 1y period for faster population
            result = await _analyze_stock_logic(symbol, period="1y")
            print(f"  -> SUCCESS: {result}")
        except Exception as e:
            print(f"  -> FAILED {symbol}: {e}")

    print("\nGenerating Market Intelligence Report...")
    try:
        intel_result = await _process_intel_logic()
        print(f"  -> SUCCESS: {intel_result}")
    except Exception as e:
        print(f"  -> FAILED INTEL: {e}")

    print("\n--- POPULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(populate())
