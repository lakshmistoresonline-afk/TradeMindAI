import os
import sys
import asyncio
from sqlalchemy import text

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def check():
    from backend.core.postgres import SessionLocal, StockDB, PriceDB, LiveSignalDB

    with SessionLocal() as session:
        total_stocks = session.query(StockDB).count()
        stocks_with_prices = session.query(PriceDB.symbol).distinct().count()
        total_prices = session.query(PriceDB).count()

        print(f"Total Stocks in 'stocks' table: {total_stocks}")
        print(f"Total Symbols in 'historical_prices' table: {stocks_with_prices}")
        print(f"Total price records: {total_prices}")

        # Check if there are symbols in historical_prices that are NOT in stocks table
        res = session.execute(text("SELECT DISTINCT symbol FROM historical_prices WHERE symbol NOT IN (SELECT symbol FROM stocks)"))
        missing_in_stocks = [r[0] for r in res]
        print(f"Symbols in prices but NOT in stocks table: {len(missing_in_stocks)}")
        if missing_in_stocks:
            print(f"  Sample: {missing_in_stocks[:10]}")

if __name__ == "__main__":
    asyncio.run(check())
