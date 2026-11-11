"""
================================================================================
TradeMindAI Integration Test: End-to-End Calibrator Artifact & Gate Rejection Proof
================================================================================
Demonstrates that:
1. Real fitted scikit-learn models and IsotonicRegression calibrator files on disk load correctly.
2. Missing, corrupt, or mismatched calibrator artifacts fail closed (`is_calibrated=False`).
3. Publication gates (SignalQualityService & SignalEngine) unconditionally reject uncalibrated predictions.
================================================================================
"""

import os
import pytest
import joblib
import asyncio
import numpy as np
import pandas as pd
import datetime
from datetime import timezone
from unittest.mock import AsyncMock, MagicMock, patch
from sklearn.dummy import DummyClassifier
from sklearn.isotonic import IsotonicRegression

from backend.domain.models.data_platform import ModelMetadata
from backend.services.ml_service import MLService
from backend.services.signal_engine import SignalEngine
from backend.services.signal_quality_service import SignalQualityService
from backend.services.equity_signal_generation_service import DynamicFeatureVector, EquitySignalGenerationService

@pytest.fixture
def calibrated_champion_metadata():
    return ModelMetadata(
        name="INFY_SWING_model_v1.joblib",
        symbol="INFY",
        version="v2.3_20260911",
        horizon="SWING",
        type="VotingClassifier",
        accuracy=0.68,
        precision=0.62,
        recall=0.60,
        f1_score=0.61,
        roc_auc=0.68,
        brier_score=0.12,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 100, "positives_test": 35, "feature_names": ["f1", "f2"]},
        calibration_metadata={"method": "isotonic", "calibrator_file": "INFY_SWING_calib.joblib", "is_calibrated": True}
    )

@pytest.fixture
def uncalibrated_champion_metadata():
    return ModelMetadata(
        name="INFY_SWING_uncalib.joblib",
        symbol="INFY",
        version="v2.3_20260911",
        horizon="SWING",
        type="VotingClassifier",
        accuracy=0.68,
        precision=0.62,
        recall=0.60,
        f1_score=0.61,
        roc_auc=0.68,
        brier_score=0.12,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 100, "positives_test": 35},
        calibration_metadata={"is_calibrated": False}
    )

@pytest.mark.asyncio
async def test_integration_real_disk_calibrator_artifact_inference(tmp_path):
    # Create and dump real scikit-learn model and calibrator artifacts to disk
    model_name = "INFY_SWING_real_model.joblib"
    calib_name = "INFY_SWING_real_calib.joblib"

    dummy = DummyClassifier(strategy="prior")
    X_dummy = pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0]})
    dummy.fit(X_dummy, pd.Series([1, 0]))

    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit([0.2, 0.8], [0.1, 0.9])

    model_path = os.path.join(str(tmp_path), model_name)
    calib_path = os.path.join(str(tmp_path), calib_name)
    joblib.dump(dummy, model_path)
    joblib.dump(calibrator, calib_path)

    champion = ModelMetadata(
        name=model_name,
        symbol="INFY",
        version="v2.3_real",
        horizon="SWING",
        type="DummyClassifier",
        accuracy=0.65,
        roc_auc=0.62,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 100, "positives_test": 30, "feature_names": ["f1", "f2"]},
        calibration_metadata={"method": "isotonic", "calibrator_file": calib_name, "is_calibrated": True}
    )

    mock_repo = AsyncMock()
    mock_repo.get_champion_model.return_value = champion

    ml_service = MLService(repository=mock_repo, model_dir=str(tmp_path))
    res = await ml_service.predict_with_champion("INFY", {"f1": 1.5, "f2": 3.5}, champion=champion)

    assert res["prediction"] in ("UP", "DOWN", "NEUTRAL")
    assert res["is_calibrated"] is True
    assert SignalQualityService.should_publish("SWING", champion, 0.65, is_calibrated=res["is_calibrated"]) is True

@pytest.mark.asyncio
async def test_integration_missing_calibrator_artifact_file_fails_closed(tmp_path):
    # Model exists but calibrator file is missing on disk
    model_name = "INFY_SWING_no_calib_file.joblib"

    dummy = DummyClassifier(strategy="prior")
    dummy.fit(pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0]}), pd.Series([1, 0]))
    joblib.dump(dummy, os.path.join(str(tmp_path), model_name))

    champion = ModelMetadata(
        name=model_name,
        symbol="INFY",
        version="v2.3_real",
        horizon="SWING",
        type="DummyClassifier",
        accuracy=0.65,
        roc_auc=0.62,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 100, "positives_test": 30, "feature_names": ["f1", "f2"]},
        calibration_metadata={"method": "isotonic", "calibrator_file": "NON_EXISTENT_CALIB.joblib", "is_calibrated": True}
    )

    mock_repo = AsyncMock()
    ml_service = MLService(repository=mock_repo, model_dir=str(tmp_path))
    res = await ml_service.predict_with_champion("INFY", {"f1": 1.5, "f2": 3.5}, champion=champion)

    assert res["is_calibrated"] is False
    assert SignalQualityService.should_publish("SWING", champion, 0.65, is_calibrated=res["is_calibrated"]) is False

@pytest.mark.asyncio
async def test_integration_corrupt_calibrator_artifact_file_fails_closed(tmp_path):
    # Model exists but calibrator file is corrupted
    model_name = "INFY_SWING_corrupt_calib.joblib"
    calib_name = "INFY_SWING_corrupt_calib_file.joblib"

    dummy = DummyClassifier(strategy="prior")
    dummy.fit(pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0]}), pd.Series([1, 0]))
    joblib.dump(dummy, os.path.join(str(tmp_path), model_name))

    # Write invalid content to calibrator file
    calib_path = os.path.join(str(tmp_path), calib_name)
    with open(calib_path, "w") as f:
        f.write("CORRUPTED_CALIBRATOR_DATA")

    champion = ModelMetadata(
        name=model_name,
        symbol="INFY",
        version="v2.3_real",
        horizon="SWING",
        type="DummyClassifier",
        accuracy=0.65,
        roc_auc=0.62,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 100, "positives_test": 30, "feature_names": ["f1", "f2"]},
        calibration_metadata={"method": "isotonic", "calibrator_file": calib_name, "is_calibrated": True}
    )

    mock_repo = AsyncMock()
    ml_service = MLService(repository=mock_repo, model_dir=str(tmp_path))
    res = await ml_service.predict_with_champion("INFY", {"f1": 1.5, "f2": 3.5}, champion=champion)

    assert res["is_calibrated"] is False
    assert SignalQualityService.should_publish("SWING", champion, 0.65, is_calibrated=res["is_calibrated"]) is False

@pytest.mark.asyncio
async def test_integration_uncalibrated_prediction_rejected_in_signal_engine(calibrated_champion_metadata):
    now_utc = datetime.datetime.now(timezone.utc)
    features = [DynamicFeatureVector(now_utc, {
        "Close": 1500.0, "close": 1500.0, "Open": 1490.0, "High": 1520.0, "Low": 1485.0, "Volume": 100000.0,
        "ema_20": 1480.0, "ema_50": 1460.0, "ema_200": 1400.0, "sma_20": 1475.0, "ATR": 25.0, "RSI": 62.0
    })]

    uncalibrated_ml_res = {
        "prediction": "UP",
        "confidence": 65.0,
        "model_version": "v2.3_20260911",
        "is_calibrated": False,
        "metadata": {
            "calibrated_probability_up": 0.65,
            "raw_probability_up": 0.65,
            "is_calibrated": False
        }
    }

    with patch("backend.core.container.container.ml_service.predict_with_champion", new_callable=AsyncMock) as mock_predict:
        mock_predict.return_value = uncalibrated_ml_res
        signal = await SignalEngine.generate_signal(
            symbol="INFY",
            asset_class="EQUITY",
            timeframe="SWING",
            features_list=features,
            champion=calibrated_champion_metadata,
            save_prediction=False,
            evaluation_timestamp=now_utc
        )

        assert signal is None

@pytest.mark.asyncio
async def test_integration_uncalibrated_model_metadata_fails_publication_gate(uncalibrated_champion_metadata):
    assert SignalQualityService.should_publish("SWING", uncalibrated_champion_metadata, 0.65, is_calibrated=True) is False
