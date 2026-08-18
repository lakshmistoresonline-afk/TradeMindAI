
import os
import sys
import asyncio
import pandas as pd
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def verify_runtime():
    print("[*] Generating Symbol Model Runtime Matrix...")

    results = []
    run_ts = datetime.utcnow()

    for symbol in NIFTY_200_CONSTITUENTS:
        data = {
            "symbol": symbol,
            "model_path": None,
            "model_version": None,
            "strategy_version": "v2.2",
            "feature_count": 0,
            "load_status": "FAILED",
            "inference_status": "FAILED",
            "error": None
        }

        try:
            # 1. Check Model Existence
            champion = await container.data_platform_repo.get_champion_model(symbol)
            if not champion:
                data["error"] = "NO_CHAMPION_IN_REGISTRY"
                results.append(data)
                continue

            data["model_version"] = champion.version
            data["model_path"] = f"backend/ml/registry/{champion.name}"

            # 2. Try Loading and Inference
            features_list = await container.data_platform_repo.get_features_by_range(
                symbol,
                run_ts - timedelta(days=7),
                run_ts
            )

            if not features_list:
                data["error"] = "NO_FEATURES_IN_STORE"
                results.append(data)
                continue

            last_features = features_list[-1].features
            data["feature_count"] = len(last_features)

            # 3. Model Load is implicit in predict_with_champion or ml_service
            ml_res = await container.ml_service.predict_with_champion(symbol, last_features)

            if "error" in ml_res and ml_res["error"]:
                data["error"] = ml_res["error"]
            else:
                data["load_status"] = "PASSED"
                data["inference_status"] = "PASSED"

        except Exception as e:
            data["error"] = str(e)

        results.append(data)

    df = pd.DataFrame(results)
    df.to_csv("symbol_model_runtime_matrix.csv", index=False)

    summary = {
        "total": len(df),
        "load_passed": len(df[df['load_status'] == 'PASSED']),
        "load_failed": len(df[df['load_status'] == 'FAILED']),
        "feature_mismatch": len(df[df['feature_count'] != 11])
    }
    print(f"\nMatrix generated. Summary: {summary}")

if __name__ == "__main__":
    asyncio.run(verify_runtime())
