import os
import sys
import asyncio
import json

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def check():
    from backend.core.postgres import SessionLocal, StockDB, PriceDB
    from sqlalchemy import desc

    with SessionLocal() as session:
        stocks = session.query(StockDB).all()
        for s in stocks[:10]:
            price = session.query(PriceDB).filter(PriceDB.symbol == s.symbol).order_by(desc(PriceDB.date)).first()
            if price:
                print(f"Symbol: {s.symbol} | Price: {price.close} | Indicators: {bool(price.indicators)}")
                if price.indicators:
                    try:
                        ind = json.loads(price.indicators)
                        print(f"  Sample: {list(ind.keys())}")
                    except:
                        print("  Indicator parse error")
            else:
                print(f"Symbol: {s.symbol} | NO PRICE DATA")

if __name__ == "__main__":
    asyncio.run(check())
