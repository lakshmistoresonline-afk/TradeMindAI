import os
import sys
import asyncio
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.workers.tasks import _analyze_stock_logic
from backend.core.postgres import StockDB, DATABASE_URL
from scripts.audit_database import NIFTY_100

# Re-create engine/session logic locally for robustness
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

async def process_batch(symbols):
    tasks = [_analyze_stock_logic(s, period="1mo") for s in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for s, r in zip(symbols, results):
        if isinstance(r, Exception): print(f"[!] Error {s}: {r}")
        else: print(f"[*] {s} Updated.")

async def run_population():
    print(f"--- TradeMind AI Universe Population Engine ---")
    session = Session()
    stocks = session.query(StockDB).all()
    db_symbols = {s.symbol for s in stocks}
    session.close()

    candidates = []
    now = datetime.datetime.now(datetime.UTC)
    freshness_threshold = datetime.timedelta(hours=24)

    # 1. Identify missing or incomplete Nifty 100 stocks
    for symbol in NIFTY_100:
        stock = next((s for s in stocks if s.symbol == symbol), None)

        if not stock:
            candidates.append(symbol)
            continue

        is_complete = stock.last_price and stock.analysis and stock.options_data and stock.financial_history and stock.health_metrics
        updated_at = stock.updated_at.replace(tzinfo=datetime.UTC) if stock.updated_at else None
        is_stale = updated_at is None or (now - updated_at) > freshness_threshold

        if not is_complete or is_stale:
            candidates.append(symbol)

    print(f"Total Universe: {len(NIFTY_100)}")
    print(f"Pending/Stale:  {len(candidates)}")

    if not candidates:
        print("Universe is 100% Complete and Fresh.")
        return

    # Process in small batches to stay within Tool/System timeouts
    BATCH_SIZE = 2
    MAX_UPDATES = 10
    updated = 0

    for i in range(0, len(candidates), BATCH_SIZE):
        if updated >= MAX_UPDATES: break
        batch = candidates[i:i+BATCH_SIZE]
        print(f"Processing Batch {i//BATCH_SIZE + 1}: {batch}")
        await process_batch(batch)
        updated += len(batch)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_population())
