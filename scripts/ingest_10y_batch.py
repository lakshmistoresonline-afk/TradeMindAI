import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

from backend.core.container import container
from backend.workers.tasks import _analyze_stock_logic
from backend.core.postgres import init_db

async def ingest():
    print("--- TradeMind AI: 10-YEAR DATA INGESTION BATCH (FINAL PASS) ---")
    init_db()

    # Final remaining symbols
    symbols = [
        "JSWSTEEL", "TITAN", "ULTRACEMCO"
    ]

    for symbol in symbols:
        try:
            print(f"Ingesting 10Y data for {symbol}...")
            await _analyze_stock_logic(symbol, period="10y")
            print(f"  ✅ {symbol}: SUCCESS")
            # Wait to clear Groq rate limits
            await asyncio.sleep(10)
        except Exception as e:
            print(f"  ❌ {symbol}: FAILED - {e}")

    print("--- BATCH COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(ingest())
