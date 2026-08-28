import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def test_problematic_symbols():
    symbols = ["PEL", "TATAMOTORS", "ZOMATO", "GMRINFRA", "L&TFH"]
    dp_repo = container.data_platform_repo

    print("\n--- NIFTY 200 DATA QUALITY TEST ---")

    for s in symbols:
        print(f"Testing {s}...")
        # 1. Parquet Check
        feats = await dp_repo.get_features_by_range(s, datetime(2020, 1, 1), datetime.utcnow())
        assert len(feats) > 100, f"Symbol {s} has insufficient features: {len(feats)}"
        print(f"   [PASS] Features count: {len(feats)}")

        # 2. Latest Data Age
        latest_ts = feats[-1].date
        age_hours = (datetime.utcnow() - latest_ts.replace(tzinfo=None)).total_seconds() / 3600.0
        print(f"   [INFO] Data Age: {age_hours:.2f} hours")

        # 3. Model Inference Check
        ml_res = await container.ml_service.predict_with_champion(s, feats[-1].features)
        if ml_res.get("prediction") == "N/A":
            print(f"   [WARN] No champion model for {s}")
        else:
            print(f"   [PASS] ML Prediction: {ml_res['prediction']} ({ml_res['confidence']}%)")

    print("\n[SUCCESS] NIFTY 200 Core Remediation Verified.")

if __name__ == "__main__":
    asyncio.run(test_problematic_symbols())
