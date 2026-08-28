import os
import sys
import asyncio
import datetime
import time
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.workers.tasks import _analyze_stock_ai_logic
from backend.core.postgres import SessionLocal, StockDB
from scripts.audit_database import NIFTY_100

async def process_ai(symbol):
    print(f"[*] Processing AI for {symbol}...")
    try:
        # Check if we have enough data before calling AI
        session = SessionLocal()
        stock = session.query(StockDB).filter(StockDB.symbol == symbol).first()
        if not stock:
            session.close()
            return "NOT_FOUND"

        # Check for required data
        if not stock.last_price or stock.last_price == 0:
            print(f"   [!] {symbol}: INSUFFICIENT_DATA (No price)")
            stock.ai_status = "INSUFFICIENT_DATA"
            stock.ai_last_error = "Missing market price for AI analysis"
            session.commit()
            session.close()
            return "INSUFFICIENT_DATA"

        session.close()

        # Run AI Analysis
        result = await _analyze_stock_ai_logic(symbol)
        print(f"   [+] AI {symbol}: {result}")

        if "RATE_LIMIT" in str(result) or "429" in str(result):
            return "RATE_LIMIT"

        return "SUCCESS" if "successful" in str(result) or "already current" in str(result) else "FAILED"

    except Exception as e:
        print(f"   [!] Error processing {symbol}: {e}")
        return "ERROR"

async def main():
    print("--- TRADEMIND AI: FULL AI PIPELINE COMPLETION ---")

    session = SessionLocal()
    # Find Nifty 100 assets that are NOT SUCCESS or INSUFFICIENT_DATA
    stocks_to_process = session.query(StockDB).filter(
        StockDB.symbol.in_(NIFTY_100),
        ~StockDB.ai_status.in_(["SUCCESS", "INSUFFICIENT_DATA"])
    ).all()
    symbols = [s.symbol for s in stocks_to_process]
    session.close()

    print(f"[*] Found {len(symbols)} pending Nifty 100 assets.")

    if not symbols:
        print("All Nifty 100 AI analyses are already complete or marked as insufficient data.")
        return

    processed = 0
    success = 0
    insufficient = 0
    failed = 0

    # Process sequentially for strict rate limiting
    for symbol in symbols:
        res = await process_ai(symbol)

        if res == "RATE_LIMIT":
            print("[!] Hitting global rate limit. Stopping for this cycle.")
            break

        processed += 1
        if res == "SUCCESS": success += 1
        elif res == "INSUFFICIENT_DATA": insufficient += 1
        else: failed += 1

        # Cooldown to keep Groq happy and manage TPD
        print("[*] Cooling down (12s)...")
        await asyncio.sleep(12)

    print(f"\n--- CYCLE COMPLETE ---")
    print(f"Processed: {processed}")
    print(f"Success:   {success}")
    print(f"Insufficient: {insufficient}")
    print(f"Failed:    {failed}")

if __name__ == "__main__":
    asyncio.run(main())
