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

from backend.workers.tasks import _sync_stock_data_logic
from backend.core.postgres import SessionLocal, StockDB

async def refresh_stock(symbol):
    print(f"[*] Refreshing {symbol}...")
    try:
        await _sync_stock_data_logic(symbol, period="1mo")
        session = SessionLocal()
        stock = session.query(StockDB).filter(StockDB.symbol == symbol).first()
        if stock:
            stock.updated_at = datetime.datetime.utcnow()
            session.commit()
        session.close()
        print(f"   [+] {symbol} Refreshed.")
        return True
    except Exception as e:
        print(f"   [!] Error refreshing {symbol}: {e}")
        return False

async def main():
    print("--- TRADEMIND AI: STALE ASSET REFRESH ---")

    session = SessionLocal()
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    stale_stocks = session.query(StockDB).filter(StockDB.updated_at < cutoff).all()
    symbols = [s.symbol for s in stale_stocks]
    session.close()

    print(f"[*] Found {len(symbols)} stale assets.")

    for symbol in symbols:
        await refresh_stock(symbol)
        await asyncio.sleep(2) # Prevent YFinance throttling

    print("\n--- REFRESH COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
