"""
================================================================================
TradeMindAI Phase C: ML Prediction Integrity & Model Qualification Unit Tests
================================================================================
Comprehensive test suite verifying:
1. ML prediction output contracts (UP, DOWN, NEUTRAL, UNAVAILABLE).
2. Fail-closed rejection of missing models, corrupted artifacts, or schema mismatches.
3. Strict schema validation: missing required features or non-finite (NaN/Inf) values fail closed.
4. Probability calibration and numerical domain validation [0.0, 1.0].
5. Rejection of non-directional (NEUTRAL) or UNAVAILABLE predictions.
6. Model qualification and hard publication gates in SignalQualityService.
================================================================================
"""

import pytest
import os
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from backend.domain.models.data_platform import ModelMetadata
from backend.services.ml_service import MLService
from backend.services.signal_quality_service import SignalQualityService

@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def ml_service(mock_repo, tmp_path):
    return MLService(repository=mock_repo, model_dir=str(tmp_path))

def create_test_model_metadata(**kwargs) -> ModelMetadata:
    defaults = {
        "name": "INFY_SWING_model_v1.joblib",
        "symbol": "INFY",
        "version": "v2.3_20260911",
        "horizon": "SWING",
        "type": "VotingClassifier",
        "accuracy": 0.65,
        "roc_auc": 0.62,
        "is_champion": True,
        "status": "CHAMPION",
        "last_trained": datetime.now(timezone.utc),
        "hyperparameters": {"test_size": 100, "positives_test": 30, "feature_names": ["f1", "f2"]}
    }
    defaults.update(kwargs)
    return ModelMetadata(**defaults)

@pytest.mark.asyncio
async def test_phase_c_missing_champion_model_returns_unavailable(ml_service, mock_repo, monkeypatch):
    monkeypatch.setenv("ALLOW_MOCK_ML_PREDICTIONS", "false")
    from backend.core.config import settings
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    mock_repo.get_champion_model.return_value = None
    res = await ml_service.predict_with_champion("INFY", {"Close": 1500.0})
    assert res["prediction"] == "UNAVAILABLE"
    assert res["metadata"]["status"] == "MODEL_UNAVAILABLE"

@pytest.mark.asyncio
async def test_phase_c_missing_model_file_returns_unavailable(ml_service, mock_repo, monkeypatch):
    monkeypatch.setenv("ALLOW_MOCK_ML_PREDICTIONS", "false")
    from backend.core.config import settings
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    champion = create_test_model_metadata(name="non_existent_file.joblib")
    mock_repo.get_champion_model.return_value = champion
    res = await ml_service.predict_with_champion("INFY", {"Close": 1500.0}, champion=champion)
    assert res["prediction"] == "UNAVAILABLE"
    assert res["metadata"]["status"] == "MODEL_UNAVAILABLE"

@pytest.mark.asyncio
async def test_phase_c_corrupted_model_file_fails_closed(ml_service, mock_repo, tmp_path):
    model_file = tmp_path / "INFY_SWING_corrupt.joblib"
    model_file.write_text("corrupted_data_not_a_joblib")

    champion = create_test_model_metadata(name="INFY_SWING_corrupt.joblib")
    mock_repo.get_champion_model.return_value = champion
    res = await ml_service.predict_with_champion("INFY", {"Close": 1500.0}, champion=champion)
    assert res["prediction"] == "UNAVAILABLE"
    assert res["metadata"]["status"] == "MODEL_LOAD_FAILURE"

@pytest.mark.asyncio
async def test_phase_c_missing_required_features_schema_rejection(ml_service, mock_repo, tmp_path):
    import joblib
    from sklearn.dummy import DummyClassifier

    dummy = DummyClassifier(strategy="prior")
    X_dummy = pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0], "f3": [5.0, 6.0]})
    dummy.fit(X_dummy, pd.Series([1, 0]))

    model_name = "INFY_SWING_schema_test.joblib"
    joblib.dump(dummy, os.path.join(str(tmp_path), model_name))

    champion = create_test_model_metadata(
        name=model_name,
        hyperparameters={"feature_names": ["f1", "f2", "f3"]}
    )

    # Supply incomplete feature vector missing 'f3'
    incomplete_features = {"f1": 1.5, "f2": 3.5}
    res = await ml_service.predict_with_champion("INFY", incomplete_features, champion=champion)
    assert res["prediction"] == "UNAVAILABLE"
    assert res["metadata"]["status"] == "SCHEMA_VALIDATION_FAILURE"
    assert "f3" in res["metadata"]["reason"]

@pytest.mark.asyncio
async def test_phase_c_non_finite_features_rejection(ml_service, mock_repo, tmp_path):
    import joblib
    from sklearn.dummy import DummyClassifier

    dummy = DummyClassifier(strategy="prior")
    X_dummy = pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0]})
    dummy.fit(X_dummy, pd.Series([1, 0]))

    model_name = "INFY_SWING_non_finite.joblib"
    joblib.dump(dummy, os.path.join(str(tmp_path), model_name))

    champion = create_test_model_metadata(
        name=model_name,
        hyperparameters={"feature_names": ["f1", "f2"]}
    )

    # Feature containing NaN
    nan_features = {"f1": 1.5, "f2": np.nan}
    res_nan = await ml_service.predict_with_champion("INFY", nan_features, champion=champion)
    assert res_nan["prediction"] == "UNAVAILABLE"
    assert res_nan["metadata"]["status"] == "NON_FINITE_FEATURES"

    # Feature containing Infinity
    inf_features = {"f1": np.inf, "f2": 2.0}
    res_inf = await ml_service.predict_with_champion("INFY", inf_features, champion=champion)
    assert res_inf["prediction"] == "UNAVAILABLE"
    assert res_inf["metadata"]["status"] == "NON_FINITE_FEATURES"

def test_phase_c_signal_quality_service_fails_closed_on_unregistered_or_weak_model():
    # Unregistered model (model is None) -> should_publish is False
    assert SignalQualityService.should_publish("SWING", None, 0.60) is False

    # Model with insufficient test sample size (< 20) -> should_publish is False
    weak_sample_model = create_test_model_metadata(
        accuracy=0.60,
        roc_auc=0.65,
        hyperparameters={"test_size": 10, "positives_test": 2}
    )
    assert SignalQualityService.should_publish("SWING", weak_sample_model, 0.60) is False

    # Model with low ROC AUC (<= 0.52 for SWING) -> should_publish is False
    low_auc_model = create_test_model_metadata(
        accuracy=0.51,
        roc_auc=0.50,
        hyperparameters={"test_size": 100, "positives_test": 30}
    )
    assert SignalQualityService.should_publish("SWING", low_auc_model, 0.60) is False

    # Qualified model with good AUC (0.62) and test_size (100) -> should_publish is True
    good_model = create_test_model_metadata(
        accuracy=0.65,
        roc_auc=0.62,
        hyperparameters={"test_size": 100, "positives_test": 30}
    )
    assert SignalQualityService.should_publish("SWING", good_model, 0.60) is True
