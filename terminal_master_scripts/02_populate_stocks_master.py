import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, StockDB
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

# Indices to track alongside the 200 stocks
INDICES = ["NIFTY", "BANKNIFTY"]

# Combined universe for population
FULL_UNIVERSE = INDICES + NIFTY_200_CONSTITUENTS

# Market Lot Sizes for major F&O symbols
LOT_SIZES = {
    "NIFTY": 25, "BANKNIFTY": 15, "FINNIFTY": 40, "RELIANCE": 250, "TCS": 175, "HDFCBANK": 550,
    "INFY": 400, "ICICIBANK": 700, "SBIN": 1500, "BHARTIARTL": 950, "AXISBANK": 625, "LT": 300,
    "ITC": 1600, "KOTAKBANK": 400, "MARUTI": 50, "TATASTEEL": 5500, "TATAMOTORS": 1425, "BAJFINANCE": 125
}

async def populate():
    db = SessionLocal()
    print(f"[*] STEP 2: Populating master table with {len(FULL_UNIVERSE)} instruments...")

    try:
<<<<<<< HEAD
        # Purge existing NIFTY 200 to ensure strict 200 count
        print("[*] Purging existing NIFTY 200 records...")
        db.query(StockDB).filter(StockDB.index_membership == "NIFTY_200").delete()

=======
>>>>>>> origin/main
        count = 0
        for sym in FULL_UNIVERSE:
            stock = db.query(StockDB).filter(StockDB.symbol == sym).first()

            is_fno = sym in LOT_SIZES or sym in INDICES
            lot = LOT_SIZES.get(sym, None)

            # Identify if it's a constituent or index
            index_membership = "NIFTY_200" if sym in NIFTY_200_CONSTITUENTS else "INDEX"

            data = {
                "symbol": sym,
                "name": f"{sym} Index" if sym in INDICES else f"{sym} Limited",
                "is_fno": is_fno,
                "lot_size": lot,
                "index_membership": index_membership,
                "index_weight": 0.0, # Initial placeholder
                "ai_status": "READY",
                "updated_at": datetime.now()
            }

            if not stock:
                db.add(StockDB(**data))
            else:
                for k, v in data.items():
                    setattr(stock, k, v)
            count += 1

        db.commit()
        print(f"[SUCCESS] Master stock population complete. Total: {count} synced.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate())
