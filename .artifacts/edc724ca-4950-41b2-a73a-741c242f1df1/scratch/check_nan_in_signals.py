import os
import sys
import asyncio
import json
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append("D:/TradeMindAI")
load_dotenv("D:/TradeMindAI/backend/.env")

async def check():
    from backend.core.postgres import engine

    cols = ['conviction', 'entry_price', 'target_price', 'stop_loss_price', 'profit_pct', 'mfe', 'mae', 'trigger_price']

    try:
        with engine.connect() as conn:
            for col in cols:
                # In Postgres, we can check for NaN using col != col or isnan()
                query = text(f"SELECT id, symbol, {col} FROM live_signals WHERE {col}::text = 'NaN' OR {col}::text = 'Infinity' OR {col}::text = '-Infinity'")
                res = conn.execute(query)
                rows = res.fetchall()
                for row in rows:
                    print(f"[!] Found non-JSON compliant value in signal {row[0]} ({row[1]}), column {col}: {row[2]}")

    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
