import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from tabulate import tabulate
from sklearn.metrics import brier_score_loss, log_loss

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

REPORT_FILE = "docs/QUANTITATIVE_VALIDATION_REPORT.md"

async def evaluate_symbol(symbol: str, features: List[Any]):
    if len(features) < 200:
        return None

    features.sort(key=lambda x: x.date)

    n = len(features)
    train_end = int(n * 0.6)
    calib_end = int(n * 0.8)

    train_feats = features[:train_end]
    calib_feats = features[train_end:calib_end]
    test_feats = features[calib_end:]

    ml_service = container.ml_service
    metadata = await ml_service.train_and_register(symbol, train_feats + calib_feats)

    actuals = []
    raw_probs = []
    calibrated_probs = []

    for f in test_feats:
        if any(pd.isna(v) for v in f.features.values()): continue
        if f.target is None or pd.isna(f.target): continue

        res = await ml_service.predict_with_champion(symbol, f.features)
        if res.get("prediction") == "N/A": continue

        cal_p = res.get("metadata", {}).get("calibrated_probability_up", 0.5)
        raw_p = res.get("metadata", {}).get("raw_probability_up", 0.5)

        actuals.append(f.target)
        raw_probs.append(raw_p)
        calibrated_probs.append(cal_p)

    if not actuals: return None

    brier_raw = brier_score_loss(actuals, raw_probs)
    brier_cal = brier_score_loss(actuals, calibrated_probs)

    # Win rate of all "direction" signals
    wins = []
    for i in range(len(actuals)):
        # Model predicts UP if prob > 0.5, DOWN if prob < 0.5
        pred = 1 if raw_probs[i] > 0.5 else 0
        wins.append(1 if pred == actuals[i] else 0)

    win_rate = np.mean(wins)

    # Expectancy calculation (Assuming 2:1 Reward:Risk)
    # E = (Win% * 2) - (Loss% * 1)
    expectancy = (win_rate * 2.0) - ((1.0 - win_rate) * 1.0)

    return {
        "symbol": symbol,
        "n_test": len(actuals),
        "brier_raw": brier_raw,
        "brier_cal": brier_cal,
        "win_rate": win_rate,
        "expectancy": expectancy,
        "improved": brier_cal < brier_raw
    }

async def run_full_validation():
    print("============================================================")
    print(" TRADEMIND AI - QUANTITATIVE VALIDATION ENGINE")
    print("============================================================")

    sample_symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "SBIN", "LICI", "ITC", "HINDUNILVR"]
    all_results = []

    for symbol in sample_symbols:
        print(f"[*] Validating {symbol}...")
        try:
            features = await container.data_platform_repo.get_features_by_range(
                symbol, datetime(2020, 1, 1), datetime.utcnow()
            )
            if not features: continue

            res = await evaluate_symbol(symbol, features)
            if res:
                all_results.append(res)
                print(f"   [DONE] Win Rate: {res['win_rate']:.2%}, Expectancy: {res['expectancy']:.2f}R")
        except Exception as e:
            print(f"   [ERROR] {symbol}: {e}")

    if not all_results: return

    df_res = pd.DataFrame(all_results)

    with open(REPORT_FILE, "w") as f:
        f.write("# Quantitative Validation Report\n\n")
        f.write(f"**Generated**: {datetime.utcnow()} UTC\n\n")

        f.write("## 1. Global Performance Summary\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"| :--- | :--- |\n")
        f.write(f"| Avg Win Rate | {df_res['win_rate'].mean():.2%} |\n")
        f.write(f"| Avg Expectancy (2:1 R:R) | {df_res['expectancy'].mean():.2f}R |\n")
        f.write(f"| Calibration Improvement | {df_res['improved'].mean():.2%} |\n\n")

        f.write("## 2. Per-Symbol Metrics\n\n")
        f.write(df_res.to_markdown(index=False))

    print(f"\n[SUCCESS] Report generated: {REPORT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_full_validation())
