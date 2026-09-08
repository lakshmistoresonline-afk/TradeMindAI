import os
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, StockDB

async def run():
    print("--- TRADEMIND OPEN DATA QUALITY AUDIT ---")

    with SessionLocal() as session:
        stocks = session.query(StockDB).filter(StockDB.index_membership == 'NIFTY_200').all()
        total = len(stocks)

        fresh_count = 0
        price_present = 0

        now = datetime.utcnow()
        for s in stocks:
            if s.last_price is not None:
                price_present += 1
                if s.updated_at and (now - s.updated_at) < timedelta(minutes=15):
                    fresh_count += 1

        report = {
            "timestamp": now.isoformat(),
            "universe": "NIFTY-200",
            "metrics": {
                "total_count": total,
                "price_availability": f"{(price_present/total*100):.1f}%" if total > 0 else "0%",
                "freshness_pct": f"{(fresh_count/total*100):.1f}%" if total > 0 else "0%",
                "stale_count": total - fresh_count
            },
            "status": "PASS" if fresh_count > 0 else "DATA_UNAVAILABLE"
        }

        with open("docs/market_data/DATA_QUALITY_REPORT.json", "w") as f:
            json.dump(report, f, indent=4)
        print("[SUCCESS] Quality report generated.")

if __name__ == "__main__":
    asyncio.run(run())
