import asyncio
import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.container import container
from backend.services.ingestion_service import IngestionService
from backend.services.feature_store import FeatureStoreService

async def main():
    symbols = ["COALINDIA", "NTPC", "YESBANK", "AXISBANK", "DALBHARAT", "ADANIENT", "ZYDUSLIFE", "UCOBANK", "BPCL", "INFY"]
    ingestor = IngestionService(container.repository, container.provider)

    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=7)

    for symbol in symbols:
        print(f"Ingesting {symbol}...")
        res = await ingestor.ingest_historical_data(symbol, start_date, end_date, "1d")
        if res["status"] == "SUCCESS":
            print(f"   [+] Ingested {res['count']} bars. Updating features...")
            # Trigger feature calculation
            try:
                await container.feature_store.update_features(symbol)
            except Exception as fe:
                print(f"   [!] Feature update failed for {symbol}: {fe}")
        else:
            print(f"   [!] Ingestion failed for {symbol}: {res.get('reason')}")

if __name__ == "__main__":
    asyncio.run(main())
