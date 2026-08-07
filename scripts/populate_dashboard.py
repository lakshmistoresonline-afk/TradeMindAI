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
    print("--- TradeMind AI: PRODUCTION DATA POPULATION SPRINT ---")

    # Initialize DB
    init_db()

    # Fixed symbols (HUL -> HINDUNILVR)
    symbols = [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "LT", "HINDUNILVR",
        "KOTAKBANK", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN", "BAJFINANCE", "ADANIENT", "SUNPHARMA", "ULTRACEMCO", "JSWSTEEL"
    ]

    print(f"Ingesting {len(symbols)} high-conviction symbols...")

    for symbol in symbols:
        try:
            print(f"Analyzing {symbol}...")
            # RC-4: Force full 10y sync for institutional completeness
            result = await _analyze_stock_logic(symbol, period="10y")
            print(f"  -> SUCCESS: {result}")
        except Exception as e:
            print(f"  -> FAILED {symbol}: {e}")

    print("\nGenerating Market Intelligence Report...")
    try:
        intel_result = await _process_intel_logic()
        print(f"  -> SUCCESS: {intel_result}")
    except Exception as e:
        print(f"  -> FAILED INTEL: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- POPULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(populate())
