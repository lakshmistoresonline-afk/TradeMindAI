
import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def smoke_test():
    repo = container.data_platform_repo
    ml_service = container.ml_service

    with container.repository.session_factory() as pg:
        from backend.core.postgres import ModelMetadataDB
        champions = pg.query(ModelMetadataDB).filter(ModelMetadataDB.is_champion == 1).all()

    symbols = [c.symbol for c in champions if "_" not in c.symbol]
    print(f"[*] Starting Smoke Test for {len(symbols)} symbols...")

    results = {"SUCCESS": 0, "FAILED": 0, "NO_FEATURES": 0}

    for symbol in symbols:
        try:
            # 1. Fetch features
            features_list = await repo.get_features_by_range(
                symbol,
                datetime.utcnow() - timedelta(days=7),
                datetime.utcnow()
            )

            if not features_list:
                results["NO_FEATURES"] += 1
                continue

            last_features = features_list[-1].features

            # 2. Run Inference
            res = await ml_service.predict_with_champion(symbol, last_features)

            if res.get("prediction") in ["UP", "DOWN", "NEUTRAL"]:
                results["SUCCESS"] += 1
            else:
                print(f"   [FAIL] {symbol}: Prediction label '{res.get('prediction')}' - Error: {res.get('error')}")
                results["FAILED"] += 1

        except Exception as e:
            print(f"   [ERROR] {symbol}: {e}")
            results["FAILED"] += 1

    print("\nSmoke Test Summary:")
    for k, v in results.items():
        print(f"   {k}: {v}")

    if results["FAILED"] == 0:
        print("\n[SUCCESS] All registered models passed inference smoke test.")
        return True
    else:
        print(f"\n[CRITICAL] {results['FAILED']} models failed smoke test.")
        return False

if __name__ == "__main__":
    asyncio.run(smoke_test())
