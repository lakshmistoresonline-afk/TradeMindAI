import os
import asyncio
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.core.container import container
from backend.services.market_data_service import MarketDataService

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

async def validate():
    print("[*] Performing Final Price Validation Audit...")

    # 1. Trigger Refresh
    await MarketDataService.sync_active_signal_prices()

    # 2. Check Results in Neon
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, symbol, entry_price, current_price, current_price_status FROM live_signals"))
        total = 0
        different = 0
        identical = 0

        print("\nActive Signal Tally:")
        for row in res:
            total += 1
            sid, sym, entry, current, status = row
            # Round to avoid float noise
            if round(entry, 2) != round(current, 2):
                different += 1
                # print(f"   [DIFF] {sym}: {entry} -> {current}")
            else:
                identical += 1
                print(f"   [WARN] {sym} is STILL IDENTICAL: {entry} == {current}")

        print(f"\nFinal Audit Summary:")
        print(f"   Total Signals: {total}")
        print(f"   Successfully Differentiated: {different}")
        print(f"   Still Identical: {identical}")
        if total > 0:
            print(f"   Success Rate: {different/total:.1%}")

if __name__ == "__main__":
    asyncio.run(validate())
