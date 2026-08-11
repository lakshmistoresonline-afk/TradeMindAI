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

from backend.workers.tasks import _sync_stock_data_logic, _analyze_stock_ai_logic
from backend.core.postgres import SessionLocal, StockDB
from scripts.audit_database import NIFTY_100

async def ai_refresh_stock(symbol):
    print(f"[*] AI Syncing {symbol}...")
    try:
        # Step 1: Run AI Analysis
        ai_result = await _analyze_stock_ai_logic(symbol)
        print(f"   [+] AI {symbol}: {ai_result}")
        return "Analysis successful" in str(ai_result) or "already current" in str(ai_result)
    except Exception as e:
        print(f"   [!] Error syncing AI for {symbol}: {e}")
        if "RATE_LIMIT" in str(e) or "429" in str(e):
            return "RATE_LIMIT"
        return False

async def main():
    print("--- TRADEMIND AI: AI ANALYSIS COMPLETION ---")

    session = SessionLocal()
    pending_stocks = session.query(StockDB).filter(StockDB.symbol.in_(NIFTY_100), StockDB.ai_status == 'PENDING').all()
    symbols = [s.symbol for s in pending_stocks]
    session.close()

    print(f"[*] Found {len(symbols)} pending AI analyses in Nifty 100.")

    if not symbols:
        print("All Nifty 100 AI analyses are already complete.")
        return

    # Process sequentially for AI to strictly avoid 429 and manage quota
    MAX_AI_RUNS = 15
    processed = 0
    for symbol in symbols:
        if processed >= MAX_AI_RUNS: break

        result = await ai_refresh_stock(symbol)
        if result == "RATE_LIMIT":
            print("[!] Hitting global rate limit. Stopping for this cycle.")
            break
        elif result:
            processed += 1
            # Cooldown between AI agents to keep Groq happy
            print("[*] Cooling down (10s)...")
            await asyncio.sleep(10)
        else:
            # Failed but not rate limit, skip to next
            continue

    print(f"\n--- AI REFRESH CYCLE COMPLETE: {processed} stocks updated ---")

if __name__ == "__main__":
    asyncio.run(main())
