import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, accuracy_score

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def audit_symbol(symbol: str):
    print(f"\n--- Forensic Audit: {symbol} ---")

    # 1. Fetch Features
    features = await container.data_platform_repo.get_features_by_range(
        symbol, datetime(2020, 1, 1), datetime(2026, 8, 14)
    )

    if len(features) < 300:
        print(f"[SKIP] {symbol} has insufficient features ({len(features)})")
        return None

    # Sort and clean
    df = pd.DataFrame([{"date": f.date, **f.features, "target": f.target} for f in features])
    df.sort_values('date', inplace=True)
    df.dropna(subset=['target'], inplace=True)
    for col in df.columns:
        if col != 'date':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    n = len(df)
    train_end = int(n * 0.6)
    calib_end = int(n * 0.8)

    train_df = df.iloc[:train_end]
    calib_df = df.iloc[train_end:calib_end]
    test_df = df.iloc[calib_end:]

    X_train = train_df.drop(['date', 'target'], axis=1)
    y_train = train_df['target'].astype(int)

    X_calib = calib_df.drop(['date', 'target'], axis=1)
    y_calib = calib_df['target'].astype(int)

    X_test = test_df.drop(['date', 'target'], axis=1)
    y_test = test_df['target'].astype(int)

    # 2. Fit Model (Oldest 60%)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 3. Fit Calibrator (Middle 20%)
    probs_calib = model.predict_proba(X_calib)[:, 1].reshape(-1, 1)
    calibrator = LogisticRegression(C=1e10)
    calibrator.fit(probs_calib, y_calib)

    # 4. Evaluate (Latest 20%)
    probs_raw = model.predict_proba(X_test)[:, 1]
    probs_calib_test = calibrator.predict_proba(probs_raw.reshape(-1, 1))[:, 1]

    brier_raw = brier_score_loss(y_test, probs_raw)
    brier_cal = brier_score_loss(y_test, probs_calib_test)

    # Win rate of raw direction (prob > 0.5)
    preds = (probs_raw > 0.5).astype(int)
    acc = accuracy_score(y_test, preds)

    print(f"Test Samples: {len(y_test)}")
    print(f"Win Rate (Direction): {acc:.2%}")
    print(f"Brier (Raw): {brier_raw:.4f}")
    print(f"Brier (Calibrated): {brier_cal:.4f}")
    print(f"Calibration Improvement: {((brier_raw - brier_cal)/brier_raw):.2%}")

    # Verify probability distribution
    print(f"Raw Probs - Unique: {len(np.unique(probs_raw))}, Mean: {probs_raw.mean():.4f}")
    print(f"Calib Probs - Unique: {len(np.unique(probs_calib_test))}, Mean: {probs_calib_test.mean():.4f}")

    return {
        "symbol": symbol,
        "win_rate": acc,
        "brier_raw": brier_raw,
        "brier_cal": brier_cal
    }

async def run():
    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY"]
    results = []
    for s in symbols:
        res = await audit_symbol(s)
        if res: results.append(res)

    if results:
        avg_wr = np.mean([r['win_rate'] for r in results])
        print(f"\nAggregate Avg Win Rate: {avg_wr:.2%}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
