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

from backend.workers.tasks import _sync_stock_data_logic, _analyze_stock_ai_logic
from backend.core.postgres import StockDB, DATABASE_URL
from scripts.audit_database import NIFTY_100

# Configuration
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

async def heal_stock(symbol: str):
    print(f"[*] Healing data for {symbol}...")
    try:
        # Phase 1: Sync all market/fundamental/options data
        await _sync_stock_data_logic(symbol, period="1y")
        # Phase 2: Run AI Analysis
        await _analyze_stock_ai_logic(symbol)
        print(f"   [+] {symbol}: DATA RECONCILED")
        return True
    except Exception as e:
        print(f"   [!] {symbol}: Healing failed: {e}")
        return False

async def main():
    print("--- TRADEMIND AI: DASHBOARD DATA CORRECTOR (HARDENED) ---")

    session = Session()
    stocks = session.query(StockDB).all()
    session.close()

    # Identify stocks with gaps
    incomplete = []
    for symbol in NIFTY_100:
        s = next((st for st in stocks if st.symbol == symbol), None)
        if not s:
            incomplete.append(symbol)
            continue

        # Audit criteria for High-Fidelity
        is_fresh = s.ai_status == "SUCCESS"
        has_struct = s.structured_consensus is not None

        if not is_fresh or not has_struct:
            incomplete.append(symbol)

    print(f"Detected {len(incomplete)} stocks requiring high-fidelity upgrade.")

    if not incomplete:
        print("All dashboard data is verified and complete.")
        return

    # Process sequentially for stability
    MAX_UPDATES = 10
    processed = 0
    for symbol in incomplete:
        if processed >= MAX_UPDATES: break

        await heal_stock(symbol)
        processed += 1

        if processed < MAX_UPDATES:
            print("Cooling down (15s)...")
            await asyncio.sleep(15)

    print(f"\n--- REPAIR CYCLE COMPLETE: {processed} stocks updated ---")

if __name__ == "__main__":
    asyncio.run(main())
