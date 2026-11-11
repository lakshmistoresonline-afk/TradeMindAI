"""
================================================================================
TradeMindAI Integration Test: End-to-End Uncalibrated Prediction Rejection Proof
================================================================================
Proves that the actual production signal-generation pipeline rejects uncalibrated predictions
end-to-end at both SignalEngine and SignalQualityService publication gates.
================================================================================
"""

import pytest
import asyncio
import datetime
from datetime import timezone
from unittest.mock import AsyncMock, MagicMock, patch

from backend.domain.models.data_platform import ModelMetadata
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
        hyperparameters={"test_size": 100, "positives_test": 35},
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
async def test_integration_uncalibrated_prediction_rejected_in_signal_engine(calibrated_champion_metadata):
    now_utc = datetime.datetime.now(timezone.utc)
    features = [DynamicFeatureVector(now_utc, {
        "Close": 1500.0, "close": 1500.0, "Open": 1490.0, "High": 1520.0, "Low": 1485.0, "Volume": 100000.0,
        "ema_20": 1480.0, "ema_50": 1460.0, "ema_200": 1400.0, "sma_20": 1475.0, "ATR": 25.0, "RSI": 62.0
    })]

    # Mock MLService predict_with_champion returning is_calibrated = False
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

        # Uncalibrated prediction must be aborted and return None
        assert signal is None

@pytest.mark.asyncio
async def test_integration_calibrated_prediction_accepted_in_signal_engine(calibrated_champion_metadata):
    now_utc = datetime.datetime.now(timezone.utc)
    features = [DynamicFeatureVector(now_utc, {
        "Close": 1500.0, "close": 1500.0, "Open": 1490.0, "High": 1520.0, "Low": 1485.0, "Volume": 100000.0,
        "ema_20": 1480.0, "ema_50": 1460.0, "ema_200": 1400.0, "sma_20": 1475.0, "ATR": 25.0, "RSI": 62.0
    })]

    calibrated_ml_res = {
        "prediction": "UP",
        "confidence": 65.0,
        "model_version": "v2.3_20260911",
        "is_calibrated": True,
        "metadata": {
            "calibrated_probability_up": 0.65,
            "raw_probability_up": 0.60,
            "is_calibrated": True
        }
    }

    mock_regime = AsyncMock()
    mock_regime.regime = "BULL"
    mock_regime.sentiment_score = 0.8

    with patch("backend.core.container.container.ml_service.predict_with_champion", new_callable=AsyncMock) as mock_predict:
        with patch("backend.core.container.container.ios_repo.get_latest_regime", new_callable=AsyncMock) as mock_get_regime:
            with patch("backend.core.container.container.repository.get_recent_prices", new_callable=AsyncMock) as mock_get_prices:
                mock_predict.return_value = calibrated_ml_res
                mock_get_regime.return_value = mock_regime
                mock_get_prices.return_value = [MagicMock()] * 20

                signal = await SignalEngine.generate_signal(
                    symbol="INFY",
                    asset_class="EQUITY",
                    timeframe="SWING",
                    features_list=features,
                    champion=calibrated_champion_metadata,
                    save_prediction=False,
                    evaluation_timestamp=now_utc
                )

                assert signal is not None
                assert signal.direction == "LONG"
                assert signal.calibrated_probability == 0.65

@pytest.mark.asyncio
async def test_integration_uncalibrated_model_metadata_fails_publication_gate(uncalibrated_champion_metadata):
    # Model metadata explicitly marked uncalibrated must fail publication gate
    assert SignalQualityService.should_publish("SWING", uncalibrated_champion_metadata, 0.65, is_calibrated=True) is False
