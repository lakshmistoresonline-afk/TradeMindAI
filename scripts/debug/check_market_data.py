import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import asyncio
import sys

sys.path.append(os.getcwd())
from backend.core.container import container

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

async def check():
    print("--- Market Data Availability Audit ---")

    # 1. Check VIX from Provider
    try:
        vix = await container.provider.get_ltp("INDIAVIX")
        print(f"Provider INDIAVIX: {vix}")
    except Exception as e:
        print(f"Provider VIX Error: {e}")

    # 2. Check NIFTY from Provider
    try:
        nifty = await container.provider.get_ltp("NIFTY")
        print(f"Provider NIFTY: {nifty}")
    except Exception as e:
        print(f"Provider NIFTY Error: {e}")

    # 3. Check DB records
    with engine.connect() as conn:
        res = conn.execute(text("SELECT DISTINCT symbol FROM historical_prices WHERE symbol IN ('NIFTY', 'BANKNIFTY', 'INDIAVIX')"))
        print("\nDB Indices Found:")
        for row in res:
            print(f"   {row[0]}")

if __name__ == "__main__":
    asyncio.run(check())
