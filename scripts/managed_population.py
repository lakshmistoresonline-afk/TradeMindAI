import os
import sys
import asyncio
import datetime
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.workers.tasks import _sync_stock_data_logic, _analyze_stock_ai_logic
from backend.core.postgres import StockDB, DATABASE_URL
from scripts.audit_database import NIFTY_100

# Configuration
BATCH_SIZE = 4
BATCH_DELAY = 20 # Seconds between batches
MAX_RETRIES = 2
RETRY_BACKOFF = 30 # Initial backoff seconds

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

async def phase_1_sync_data():
    print(f"\n=== PHASE 1: NON-AI DATA SYNC ===")
    for i, symbol in enumerate(NIFTY_100):
        print(f"[{i+1}/{len(NIFTY_100)}] Syncing {symbol}...")
        try:
            await _sync_stock_data_logic(symbol, period="1y")
        except Exception as e:
            print(f"   [!] Error syncing {symbol}: {e}")
        await asyncio.sleep(0.5)
    print("PHASE 1 COMPLETE.")

async def phase_2_ai_analysis():
    print(f"\n=== PHASE 2: AI ANALYSIS HUB (Rate Limit Managed) ===")

    session = Session()
    # Find stocks needing AI
    stocks = session.query(StockDB).filter(StockDB.ai_status != "SUCCESS").all()
    pending_symbols = [s.symbol for s in stocks if s.symbol in NIFTY_100]
    session.close()

    print(f"Total Nifty 100 needing AI: {len(pending_symbols)}")

    if not pending_symbols:
        print("All stocks already analyzed.")
        return

    processed = 0
    MAX_UPDATES = 40
    while processed < len(pending_symbols) and processed < MAX_UPDATES:
        batch = pending_symbols[processed : processed + BATCH_SIZE]
        print(f"\n--- Processing Batch: {batch} ({processed + 1}/{len(pending_symbols)}) ---")

        tasks = []
        for symbol in batch:
            tasks.append(process_ai_with_retry(symbol))

        await asyncio.gather(*tasks)

        processed += len(batch)
        if processed < len(pending_symbols):
            print(f"Waiting {BATCH_DELAY}s for next batch...")
            await asyncio.sleep(BATCH_DELAY)

async def process_ai_with_retry(symbol: str):
    retries = 0
    backoff = RETRY_BACKOFF

    while retries < MAX_RETRIES:
        try:
            print(f"   [*] AI Analyzing {symbol} (Attempt {retries + 1})...")
            result = await _analyze_stock_ai_logic(symbol)
            if "Analysis successful" in result:
                print(f"   [+] {symbol}: SUCCESS")
                return
            else:
                print(f"   [-] {symbol}: {result}")
                return
        except Exception as e:
            err_msg = str(e)
            if "RATE_LIMIT" in err_msg or "429" in err_msg:
                print(f"   [!] {symbol}: Rate limit hit. Backing off {backoff}s...")
                await asyncio.sleep(backoff)
                retries += 1
                backoff *= 2 # Exponential backoff
            else:
                print(f"   [!] {symbol}: Unrecoverable Error: {err_msg}")
                return

async def main():
    start_time = time.time()

    # Check if we should skip Phase 1 (if data is already synced)
    skip_p1 = "--skip-p1" in sys.argv
    if not skip_p1:
        await phase_1_sync_data()

    await phase_2_ai_analysis()

    end_time = time.time()
    duration = (end_time - start_time) / 60
    print(f"\n=== POPULATION RUN COMPLETE in {duration:.1f} minutes ===")

if __name__ == "__main__":
    asyncio.run(main())
