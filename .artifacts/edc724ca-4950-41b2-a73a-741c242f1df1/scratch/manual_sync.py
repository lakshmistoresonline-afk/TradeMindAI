import os
import sys
import asyncio

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def sync_some():
    from backend.workers.tasks import _sync_stock_data_logic
    from scripts.audit_database import NIFTY_100

    # Just sync 15 stocks to have something to work with
    symbols = NIFTY_100[:15]
    print(f"Syncing {len(symbols)} stocks...")

    for symbol in symbols:
        try:
            print(f"Syncing {symbol}...")
            await _sync_stock_data_logic(symbol, period="1y")
        except Exception as e:
            print(f"Error syncing {symbol}: {e}")

    print("Sync complete.")

if __name__ == "__main__":
    asyncio.run(sync_some())
