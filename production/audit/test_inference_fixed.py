
import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def test():
    repo = container.data_platform_repo
    ml_service = container.ml_service

    with container.repository.session_factory() as pg:
        from backend.core.postgres import ModelMetadataDB
        champions = pg.query(ModelMetadataDB).filter(ModelMetadataDB.is_champion == 1).all()

    print(f"Total champions in DB: {len(champions)}")

    symbols = []
    for c in champions:
        if "_" not in c.symbol:
            symbols.append(c.symbol)

    print(f"Pure symbols to test: {len(symbols)}")

    success = 0
    failed = 0
    skipped = 0

    for symbol in symbols:
        try:
            # Get last features
            features_list = await repo.get_features_by_range(
                symbol,
                datetime(2026, 8, 10),
                datetime.utcnow()
            )

            if not features_list:
                # print(f"   [SKIP] No features for {symbol}")
                skipped += 1
                continue

            last_features = features_list[-1].features

            res = await ml_service.predict_with_champion(symbol, last_features)
            if res.get("prediction") != "ERROR" and res.get("prediction") != "N/A":
                success += 1
            else:
                print(f"   [FAIL] {symbol}: {res.get('error', 'Unknown Error')}")
                failed += 1
        except Exception as e:
            print(f"   [ERROR] {symbol}: {e}")
            failed += 1

    print(f"Summary: Success={success}, Failed={failed}, Skipped={skipped}")

if __name__ == "__main__":
    asyncio.run(test())
