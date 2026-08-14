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

    print(f"Connecting to: {engine.url}")
    try:
        with engine.connect() as conn:
            # Check tables
            res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [r[0] for r in res]
            print(f"Tables: {tables}")

            if "live_signals" in tables:
                res = conn.execute(text("SELECT count(*) FROM live_signals"))
                count = res.scalar()
                print(f"Live Signals Count: {count}")

                if count > 0:
                    res = conn.execute(text("SELECT * FROM live_signals LIMIT 1"))
                    row = res.fetchone()
                    print(f"Sample Signal: {row}")
            else:
                print("[!] live_signals table MISSING")

    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
