import os
import sys
import asyncio
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append("D:/TradeMindAI")
load_dotenv("D:/TradeMindAI/backend/.env")

async def check():
    from backend.core.postgres import engine

    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'live_signals' ORDER BY ordinal_position"))
            cols = res.fetchall()
            for c in cols:
                print(f"Column: {c[0]} ({c[1]})")

    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
