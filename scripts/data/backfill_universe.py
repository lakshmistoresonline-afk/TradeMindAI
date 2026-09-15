import asyncio
import datetime
import sys
import os

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.core.container import container
from backend.services.universe_service import UniverseService
from backend.services.ingestion_service import IngestionService

async def backfill():
    print("=== [PHASE 2] Backfilling NIFTY-200 Universe ===")

    symbols = UniverseService.NIFTY_200_CONSTITUENTS
    ingestion_service = IngestionService(container.repository, container.provider)

    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=3 * 365)

    # 1. Sync Universe
    await UniverseService(container.repository, container.provider).sync_universe()

    # 2. Ingest
    for symbol in symbols:
        try:
            res = await ingestion_service.ingest_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval="1d"
            )
            if res["status"] == "SUCCESS":
                print(f"   [OK] {symbol}: {res['count']} candles ingested.")
            else:
                print(f"   [!] {symbol}: FAILED - {res['reason']}")
        except Exception as e:
            print(f"   [ERROR] {symbol}: {e}")

if __name__ == "__main__":
    asyncio.run(backfill())
