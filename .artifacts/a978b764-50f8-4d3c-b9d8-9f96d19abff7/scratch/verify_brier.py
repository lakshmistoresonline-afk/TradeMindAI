import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import json
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

async def verify():
    print("============================================================")
    print(" BRIER SCORE INDEPENDENT VERIFICATION")
    print("============================================================")

    # Since predictions table doesn't have the outcome (target) directly,
    # we need to join with historical_prices to get the actual 5-day forward return.
    # Or easier: just run the validation logic again but print the intermediate Brier components.

    symbol = "RELIANCE"
    features = await container.data_platform_repo.get_features_by_range(
        symbol, datetime(2020, 1, 1), datetime.utcnow()
    )

    if not features:
        print("No features for RELIANCE")
        return

    # Reproduce the test split
    features.sort(key=lambda x: x.date)
    n = len(features)
    calib_end = int(n * 0.8)
    test_feats = features[calib_end:]

    ml_service = container.ml_service

    actuals = []
    raw_probs = []
    calibrated_probs = []

    for f in test_feats:
        if f.target is None: continue
        res = await ml_service.predict_with_champion(symbol, f.features)

        cal_p = res.get("metadata", {}).get("calibrated_probability_up", 0.5)
        raw_p = res.get("metadata", {}).get("raw_probability_up", 0.5)

        actuals.append(f.target)
        raw_probs.append(raw_p)
        calibrated_probs.append(cal_p)

    if not actuals:
        print("No actuals found in test set.")
        return

    actuals = np.array(actuals)
    raw_probs = np.array(raw_probs)
    calibrated_probs = np.array(calibrated_probs)

    print(f"Actuals NaNs: {np.isnan(actuals).sum()}")
    print(f"Raw Probs NaNs: {np.isnan(raw_probs).sum()}")
    print(f"Calib Probs NaNs: {np.isnan(calibrated_probs).sum()}")

    print(f"Sample Raw Probs: {raw_probs[:10]}")
    print(f"Sample Calib Probs: {calibrated_probs[:10]}")
    print(f"Sample Actuals: {actuals[:10]}")

    brier_raw = np.nanmean((raw_probs - actuals)**2)
    brier_cal = np.nanmean((calibrated_probs - actuals)**2)

    print(f"Symbol: {symbol}")
    print(f"Samples: {len(actuals)}")
    print(f"Calculated Brier (Raw): {brier_raw:.4f}")
    print(f"Calculated Brier (Calibrated): {brier_cal:.4f}")

if __name__ == "__main__":
    from backend.core.container import container
    from datetime import datetime
    import asyncio
    asyncio.run(verify())
