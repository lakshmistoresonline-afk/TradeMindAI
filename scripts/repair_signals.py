import os
import sys
import asyncio
import json
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import SessionLocal, StockDB
from backend.core.container import container
from backend.workers.tasks import _analyze_stock_ai_logic

async def repair_signals():
    print("--- SIGNAL REPAIR ENGINE STARTING ---")
    session = SessionLocal()
    try:
        # 1. Identify stocks with missing analysis or invalid targets (NaN)
        stocks = session.query(StockDB).all()
        to_repair = []

        for s in stocks:
            has_error = s.ai_status == "FAILED"
            is_empty = s.analysis is None or s.structured_consensus is None

            # Check for NaN in targets/stops
            has_nan = False
            if s.structured_consensus:
                try:
                    sc = json.loads(s.structured_consensus)
                    if sc.get('target') is None or sc.get('stop_loss') is None:
                        has_nan = True
                except:
                    has_nan = True

            if has_error or is_empty or has_nan:
                to_repair.append(s.symbol)

        print(f"Found {len(to_repair)} stocks requiring AI reconciliation.")
        print(f"Symbols: {to_repair}")

        for symbol in to_repair:
            print(f"[*] Force-Reconciling {symbol}...")
            # Run the AI logic (This will regenerate structured_consensus with proper escaping)
            result = await _analyze_stock_ai_logic(symbol)
            print(f"[+] {symbol}: {result}")
            await asyncio.sleep(2) # Protect Rate Limits

    except Exception as e:
        print(f"Repair failed: {e}")
    finally:
        session.close()

    print("--- REPAIR COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(repair_signals())
