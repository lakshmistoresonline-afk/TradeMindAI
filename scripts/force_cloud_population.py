import asyncio
import os
import sys
import datetime
from dotenv import load_dotenv
from sqlalchemy import text, create_engine

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment EXPLICITLY
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

from backend.core.container import container
from backend.workers.tasks import _analyze_stock_logic, _process_intel_logic
from backend.core.postgres import init_db

async def populate():
    url = os.getenv("POSTGRES_URL")
    print(f"\n--- TradeMind AI: FORCED CLOUD POPULATION ---")
    print(f"Targeting: {url.split('@')[-1] if url else 'MISSING'}")

    if not url or "sqlite" in url:
        print("❌ ERROR: POSTGRES_URL is not pointing to Cloud SQL. Aborting.")
        return

    init_db()

    # Target symbols that are currently missing research DNA
    symbols = [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
        "SBIN", "BHARTIARTL", "ITC", "LT", "HINDUNILVR",
        "AXISBANK", "KOTAKBANK", "ASIANPAINT", "MARUTI", "TITAN"
    ]

    print(f"Ingesting {len(symbols)} stocks...")

    for symbol in symbols:
        try:
            print(f"Analyzing {symbol}...")
            # Use 1y for speed
            await _analyze_stock_logic(symbol, period="1y")

            # Pulse log
            print(f"  ✅ {symbol}: SUCCESS")

            # 10s cooldown
            await asyncio.sleep(10)
        except Exception as e:
            print(f"  ❌ {symbol}: FAILED - {e}")

    print("\n--- FINALIZING MARKET INTELLIGENCE ---")
    await _process_intel_logic()

    with engine.connect() as conn:
        r_count = conn.execute(text("SELECT count(*) FROM market_regimes")).scalar()
        i_count = conn.execute(text("SELECT count(*) FROM intel_reports")).scalar()
        print(f"✅ Market Intelligence: {r_count} Regimes, {i_count} Reports in SQL.")

if __name__ == "__main__":
    asyncio.run(populate())
