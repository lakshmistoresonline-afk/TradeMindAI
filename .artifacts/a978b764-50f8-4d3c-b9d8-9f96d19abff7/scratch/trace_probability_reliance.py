import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from datetime import datetime

async def trace():
    print("============================================================")
    print(" PROBABILITY TRACE & BRIER VERIFICATION: RELIANCE")
    print("============================================================")

    symbol = "RELIANCE"
    features = await container.data_platform_repo.get_features_by_range(
        symbol, datetime(2020, 1, 1), datetime(2026, 8, 14)
    )

    if not features:
        print("No features for RELIANCE")
        return

    # Reproduce the test split (60% Train, 20% Calib, 20% Test)
    features.sort(key=lambda x: x.date)
    df = pd.DataFrame([{"date": f.date, **f.features, "target": f.target} for f in features])
    df.dropna(subset=['target'], inplace=True)

    n = len(df)
    calib_end = int(n * 0.8)
    test_df = df.iloc[calib_end:]

    ml_service = container.ml_service

    trace_data = []

    for idx, row in test_df.iterrows():
        # Get features for prediction
        f_vec = row.drop(['date', 'target']).to_dict()
        res = await ml_service.predict_with_champion(symbol, f_vec)

        raw_p = res.get("metadata", {}).get("raw_probability_up", 0.5)
        cal_p = res.get("metadata", {}).get("calibrated_probability_up", 0.5)

        trace_data.append({
            "timestamp": row['date'],
            "raw_probability": raw_p,
            "calibrated_probability": cal_p,
            "actual_outcome": row['target']
        })

    trace_df = pd.DataFrame(trace_data)

    print("\n--- Statistics (N={}) ---".format(len(trace_df)))
    stats = {
        "Raw Prob Min": trace_df['raw_probability'].min(),
        "Raw Prob Max": trace_df['raw_probability'].max(),
        "Raw Prob Mean": trace_df['raw_probability'].mean(),
        "Raw Prob Median": trace_df['raw_probability'].median(),
        "Raw Prob Std": trace_df['raw_probability'].std(),
        "Calib Prob Mean": trace_df['calibrated_probability'].mean(),
        "Calib Prob Unique Count": trace_df['calibrated_probability'].nunique()
    }
    for k, v in stats.items():
        print(f"{k}: {v}")

    # Independent Brier Calculation
    brier_raw = np.mean((trace_df['raw_probability'] - trace_df['actual_outcome'])**2)
    brier_cal = np.mean((trace_df['calibrated_probability'] - trace_df['actual_outcome'])**2)

    print("\n--- Brier Score Verification ---")
    print(f"Calculated Brier (Raw): {brier_raw:.6f}")
    print(f"Calculated Brier (Calibrated): {brier_cal:.6f}")

    # Check if Brier Calibrated is better than Brier Raw
    if brier_cal < brier_raw:
        print("[PASS] Calibration improved Brier score.")
    else:
        print("[FAIL] Calibration did NOT improve Brier score.")

    print("\n--- Sample Trace (First 20) ---")
    print(trace_df.head(20).to_markdown(index=False))

if __name__ == "__main__":
    import asyncio
    asyncio.run(trace())
