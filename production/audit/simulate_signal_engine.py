
import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def simulate():
    repo = container.repository
    data_repo = container.data_platform_repo
    ml_service = container.ml_service

    results = {}

    for symbol in NIFTY_200_CONSTITUENTS:
        reason = "UNKNOWN"
        try:
            # 1. Check Model in DB
            champion = await data_repo.get_champion_model(symbol)
            if not champion:
                reason = "NO_MODEL_IN_DB"
            else:
                # 2. Check features
                features_list = await data_repo.get_features_by_range(
                    symbol,
                    datetime.utcnow() - timedelta(days=7),
                    datetime.utcnow()
                )
                if not features_list:
                    reason = "NO_FEATURES"
                else:
                    last_features = features_list[-1].features
                    last_date = features_list[-1].date

                    # 3. Check Freshness
                    if (datetime.utcnow() - last_date).total_seconds() > 86400:
                        reason = "STALE_DATA"
                    else:
                        # 4. Check Inference
                        ml_res = await ml_service.predict_with_champion(symbol, last_features)
                        if ml_res.get("prediction") == "ERROR":
                            reason = f"INFERENCE_ERROR: {ml_res.get('error')}"
                        else:
                            # 5. Check Liquidity
                            stock = await repo.get_stock_by_symbol(symbol)
                            if stock and stock.avg_volume and stock.avg_volume < 10_000_000:
                                reason = "LOW_LIQUIDITY"
                            else:
                                reason = "VALID_EVALUATION"
        except Exception as e:
            reason = f"EXCEPTION: {str(e)}"

        results[reason] = results.get(reason, 0) + 1
        if reason != "NO_MODEL_IN_DB":
            print(f"{symbol}: {reason}")

    print("\nSummary:")
    for k, v in results.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    asyncio.run(simulate())
