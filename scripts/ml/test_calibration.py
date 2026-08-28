import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.domain.models.data_platform import FeatureVector

async def test_calibration():
    print("============================================================")
    print(" PROBABILITY CALIBRATION TEST (PLATT SCALING)")
    print("============================================================")

    symbol = "RELIANCE"
    print(f"[*] Testing with {symbol}...")

    # 1. Check if model exists
    ml_service = container.ml_service

    # 2. Mock some features for test (or fetch real ones if available)
    # For a real test, we need features. Let's see if we have them.
    features = await container.data_platform_repo.get_features_by_range(
        symbol,
        datetime(2020, 1, 1),
        datetime.utcnow()
    )

    if not features or len(features) < 150:
        print(f"[!] Insufficient features found ({len(features) if features else 0}). Generating synthetic features for logic validation...")
        import numpy as np
        features = []
        start_date = datetime(2024, 1, 1)
        for i in range(200):
            features.append(FeatureVector(
                symbol=symbol,
                date=start_date + timedelta(days=i),
                version="v1",
                features={"f1": np.random.random(), "f2": np.random.random()},
                target=1.0 if np.random.random() > 0.5 else 0.0
            ))

    # 3. Train with Calibration
    print(f"[*] Training and Calibrating {symbol}...")
    metadata = await ml_service.train_and_register(symbol, features)

    print(f"\n[SUCCESS] Calibration Metadata:")
    print(f"   Method: {metadata.calibration_metadata['method']}")
    print(f"   Brier Score (Raw): {metadata.calibration_metadata['brier_score_raw']:.4f}")
    print(f"   Brier Score (Calibrated): {metadata.calibration_metadata['brier_score_calibrated']:.4f}")
    print(f"   Log Loss (Calibrated): {metadata.calibration_metadata['log_loss_calibrated']:.4f}")
    print(f"   Params: {metadata.calibration_metadata['params']}")

    # 4. Test Inference
    print(f"\n[*] Testing Inference...")
    test_vec = features[-1].features
    res = await ml_service.predict_with_champion(symbol, test_vec)
    print(f"   Result: {res}")

    if res.get("is_calibrated"):
        print("   [PASS] Calibration applied in inference.")
    else:
        print("   [FAIL] Calibration NOT applied in inference.")

if __name__ == "__main__":
    asyncio.run(test_calibration())
