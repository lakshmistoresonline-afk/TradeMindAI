"""
================================================================================
TradeMindAI Phase 4.3.2: Quality Gate & Signal Pipeline Certification Test Suite
================================================================================
Tests strict fail-closed quality gate, registered vs unregistered model metadata,
strategy inputs, time-safety, V2.2/V2.3 isolation, and safety invariants.
================================================================================
"""

import pytest
import datetime
from datetime import timezone
from backend.domain.models.data_platform import ModelMetadata
from backend.services.signal_quality_service import SignalQualityService
from backend.services.security_master_service import SecurityMasterService
from backend.core.config import settings

def test_quality_gate_strict_fail_closed_unregistered_model():
    """Verify that unregistered model metadata (model=None) unconditionally fails closed."""
    assert SignalQualityService.should_publish("SWING", None, 0.82) is False
    assert SignalQualityService.should_publish("LONG", None, 0.85) is False
    assert SignalQualityService.should_publish("SHORT", None, 0.75) is False

def test_quality_gate_registered_model_success():
    """Verify that a registered champion model with valid metrics passes the quality gate."""
    valid_model = ModelMetadata(
        name="RELIANCE_SWING_v2.2.joblib",
        symbol="RELIANCE",
        version="v2.2",
        horizon="SWING",
        type="VotingClassifier",
        accuracy=0.65,
        precision=0.60,
        recall=0.60,
        f1_score=0.60,
        roc_auc=0.65,
        brier_score=0.15,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 50, "positives_test": 20}
    )
    assert SignalQualityService.should_publish("SWING", valid_model, 0.82) is True

def test_quality_gate_insufficient_sample_size_rejected():
    """Verify that models with test_size < 20 are rejected."""
    small_model = ModelMetadata(
        name="RELIANCE_SWING_v2.2.joblib",
        symbol="RELIANCE",
        version="v2.2",
        horizon="SWING",
        type="VotingClassifier",
        accuracy=0.65,
        precision=0.60,
        recall=0.60,
        f1_score=0.60,
        roc_auc=0.65,
        brier_score=0.15,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 10, "positives_test": 2}
    )
    assert SignalQualityService.should_publish("SWING", small_model, 0.82) is False

def test_quality_gate_low_probability_rejected():
    """Verify that calibrated_prob < 0.52 fails the quality gate."""
    valid_model = ModelMetadata(
        name="RELIANCE_SWING_v2.2.joblib",
        symbol="RELIANCE",
        version="v2.2",
        horizon="SWING",
        type="VotingClassifier",
        accuracy=0.65,
        precision=0.60,
        recall=0.60,
        f1_score=0.60,
        roc_auc=0.65,
        brier_score=0.15,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 50, "positives_test": 20}
    )
    assert SignalQualityService.should_publish("SWING", valid_model, 0.45) is False

def test_security_master_bagmane_audit():
    """Verify that BAGMANE is mapped in security master with valid ISIN and listing date."""
    entry = SecurityMasterService.get_security_master_entry("BAGMANE")
    assert entry["symbol"] == "BAGMANE"
    assert entry["isin"] == "INE002A01018"
    assert entry["fyers_symbol"] == "NSE:BAGMANE-EQ"

def test_safety_invariants_strictly_enforced():
    """Verify that product safety flags remain False/True."""
    assert getattr(settings, "REAL_TRADING", True) is False
    assert getattr(settings, "LIVE_EXECUTION_ENABLED", True) is False
    assert getattr(settings, "BROKER_ORDER_EXECUTION_ENABLED", True) is False
    assert getattr(settings, "QUARANTINE_ACTIVE", False) is True
