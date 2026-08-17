import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, StockDB, engine
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

def get_historical_stats():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM historical_prices")).scalar()
        symbols = conn.execute(text("SELECT count(DISTINCT symbol) FROM historical_prices")).scalar()
        return res, symbols

async def populate():
    print(f"============================================================")
    print(f" TRADEMIND AI - STOCK MASTER SYNCHRONIZATION")
    print(f"============================================================")

    # 1. Pre-flight Protection
    initial_candles, initial_symbols = get_historical_stats()
    print(f"[*] Pre-flight: {initial_candles} candles across {initial_symbols} symbols detected.")

    db = SessionLocal()
    print(f"[*] STEP 2: Synchronizing master table with {len(FULL_UNIVERSE)} instruments...")

    try:
        # P0 HARDENING: DO NOT PURGE. Use Idempotent UPSERT.
        # This prevents accidental cascading deletes of historical data.

        # We can optionally mark symbols NOT in FULL_UNIVERSE as INACTIVE instead of deleting them.
        # But for now, we just ensure existing ones are updated.

        synced_count = 0
        new_count = 0
        updated_count = 0

        for sym in FULL_UNIVERSE:
            stock = db.query(StockDB).filter(StockDB.symbol == sym).first()

            is_fno = sym in LOT_SIZES or sym in INDICES
            lot = LOT_SIZES.get(sym, None)

            index_membership = "NIFTY_200" if sym in NIFTY_200_CONSTITUENTS else "INDEX"

            data = {
                "symbol": sym,
                "name": f"{sym} Index" if sym in INDICES else f"{sym} Limited",
                "is_fno": is_fno,
                "lot_size": lot,
                "index_membership": index_membership,
                "updated_at": datetime.now()
            }

            if not stock:
                # Add "READY" status only for new records
                data["ai_status"] = "READY"
                data["index_weight"] = 0.0
                db.add(StockDB(**data))
                new_count += 1
            else:
                # Update existing record
                for k, v in data.items():
                    setattr(stock, k, v)
                updated_count += 1

            synced_count += 1

        db.commit()
        print(f"[SUCCESS] Master sync complete. Total: {synced_count} (New: {new_count}, Updated: {updated_count})")

        # 2. Post-flight Verification
        final_candles, final_symbols = get_historical_stats()
        print(f"[*] Post-flight: {final_candles} candles across {final_symbols} symbols detected.")

        if final_candles < initial_candles:
            print(f" [!] CRITICAL ERROR: Historical data regression detected during master sync!")
            print(f"     {initial_candles} -> {final_candles} rows.")
            sys.exit(1)

        if final_symbols < initial_symbols:
            print(f" [!] WARNING: Distinct symbols with history decreased!")
            print(f"     {initial_symbols} -> {final_symbols} symbols.")
            # We don't necessarily fail here if rows are same, but it's suspicious.

    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate())
