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

    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT id, symbol, events FROM live_signals WHERE events IS NOT NULL"))
            rows = res.fetchall()
            for row in rows:
                sid, symbol, events_str = row
                if not events_str: continue
                try:
                    events = json.loads(events_str)
                    if isinstance(events, list):
                        for e in events:
                            # Check price
                            price = e.get("price")
                            if price is not None:
                                if isinstance(price, float):
                                    import math
                                    if math.isnan(price) or math.isinf(price):
                                        print(f"[!] Found NaN/Inf price in signal {sid} ({symbol})")

                            # Check metadata
                            metadata = e.get("metadata")
                            if isinstance(metadata, dict):
                                for k, v in metadata.items():
                                    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                                        print(f"[!] Found NaN/Inf metadata value in signal {sid} ({symbol})")
                except Exception as ex:
                    print(f"Error parsing events for {sid}: {ex}")

    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
