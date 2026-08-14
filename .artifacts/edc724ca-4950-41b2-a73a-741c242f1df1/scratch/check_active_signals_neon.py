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
            res = conn.execute(text("SELECT count(*) FROM live_signals WHERE status IN ('ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED')"))
            count = res.scalar()
            print(f"Active Live Signals Count: {count}")

            if count > 0:
                res = conn.execute(text("SELECT * FROM live_signals WHERE status IN ('ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED') LIMIT 3"))
                rows = res.fetchall()
                for i, row in enumerate(rows):
                    print(f"Active Signal {i}: {row}")

    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
