import asyncio
import os
import sys
import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.container import container
from backend.workers.tasks import _analyze_stock_logic
from backend.core.postgres import SessionLocal, init_db, StockDB, PriceDB

async def test_run():
    print("--- HYBRID ARCHITECTURE TEST RUN ---")

    # 1. Ensure DB is initialized
    init_db()

    symbol = "RELIANCE"
    print(f"Triggering Analysis for {symbol}...")

    try:
        # Run the internal logic directly
        result = await _analyze_stock_logic(symbol, period="1y")
        print(f"Analysis Complete! Consensus: {result}")

        # 2. Verify Persistence in SQLite
        pg = SessionLocal()
        stock = pg.query(StockDB).filter(StockDB.symbol == symbol).first()
        if stock:
            print(f"✅ Stock successfully saved to SQL: {stock.symbol}")
            print(f"   Score: {stock.ai_investment_score}, Grade: {stock.ai_investment_grade}")
        else:
            print("❌ Stock NOT found in SQL!")

        # 3. Verify Prices
        price_count = pg.query(PriceDB).filter(PriceDB.symbol == symbol).count()
        print(f"✅ Price records in SQL: {price_count}")

        # 4. Verify Parquet (DuckDB)
        feature_path = f"backend/data/features/{symbol}.parquet"
        if os.path.exists(feature_path):
            print(f"✅ Feature vectors saved to Parquet: {feature_path}")
        else:
            print("❌ Parquet file NOT found!")

        pg.close()

    except Exception as e:
        print(f"❌ Analysis Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_run())
