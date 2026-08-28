import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB, StockDB

def debug():
    db = SessionLocal()
    try:
        # Simulate API logic
        signals = db.query(LiveSignalDB).filter(
            LiveSignalDB.status.in_(["ACTIVE", "WAITING_FOR_ENTRY", "ENTRY_TRIGGERED"])
        ).order_by(LiveSignalDB.timestamp.desc()).limit(100).all()

        stocks = db.query(StockDB).all()
        stock_map = {s.symbol: {"symbol": s.symbol, "name": s.name} for s in stocks}

        for s in signals:
            stock_info = stock_map.get(s.symbol, {})
            # Simulate LS object passed to frontend
            ls_data = {
                "symbol": s.symbol,
                "asset_class": s.asset_class,
                "status": s.status,
                "conviction": s.conviction,
                "rating": s.rating
            }

            # The spread {...stockInfo, ...ls}
            merged = {**stock_info, **ls_data}

            # Check asset_class
            print(f"Symbol: {s.symbol} | DB Class: {s.asset_class} | Merged Class: {merged.get('asset_class')}")

    finally:
        db.close()

if __name__ == "__main__":
    debug()
