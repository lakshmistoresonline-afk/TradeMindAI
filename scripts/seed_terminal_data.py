import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.workers.tasks import _process_intel_logic, _refresh_rankings_logic, _analyze_stock_ai_logic

async def main():
    print("--- TRADEMIND AI: TERMINAL DATA SEEDER ---")

    # 1. Market Intelligence & Regimes
    await _process_intel_logic()

    # 2. Opportunities & Rankings
    await _refresh_rankings_logic()

    # 3. High-Conviction AI Analysis (Seed some predictions and notes)
    top_stocks = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]
    print(f"[*] Seeding AI Intelligence for: {top_stocks}")
    for symbol in top_stocks:
        try:
            # This will trigger ML predictions and potentially generate research notes
            await _analyze_stock_ai_logic(symbol)
            print(f"   [+] AI Seeded: {symbol}")
        except Exception as e:
            print(f"   [!] AI Seed Error {symbol}: {e}")

    print("\n--- SEEDING COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
