
import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def check_freshness():
    repo = container.data_platform_repo

    with container.repository.session_factory() as pg:
        from backend.core.postgres import StockDB
        symbols = [s.symbol for s in pg.query(StockDB.symbol).all()]

    now = datetime.utcnow()
    stale = []
    ready = 0

    for symbol in symbols:
        features_list = await repo.get_features_by_range(
            symbol,
            now - timedelta(days=7),
            now
        )

        if not features_list:
            stale.append((symbol, "NO_DATA"))
            continue

        last_date = features_list[-1].date
        age_hrs = (now - last_date).total_seconds() / 3600.0

        if age_hrs > 24:
            stale.append((symbol, f"{age_hrs:.1f}h"))
        else:
            ready += 1

    print(f"Freshness Report [{now}]:")
    print(f"   READY symbols (<24h): {ready}")
    print(f"   STALE symbols (>24h): {len(stale)}")

    if stale:
        print("\nStale Symbols:")
        for sym, age in stale:
            print(f"   {sym}: {age}")

if __name__ == "__main__":
    asyncio.run(check_freshness())
