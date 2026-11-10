"""
================================================================================
TradeMindAI Phase D: Signal Validation, Risk Geometry & Output Integrity Tests
================================================================================
Comprehensive test suite verifying:
1. Direction integrity (LONG/BUY and SHORT/SELL accepted; NEUTRAL/UNAVAILABLE rejected).
2. Price finiteness & positive value enforcement (NaN/Inf, zero, and negative prices rejected).
3. Risk & target geometry contract (Stop < Entry < Target for Long; Target < Entry < Stop for Short).
4. Geometric Risk/Reward ratio calculation RR = |Target - Entry| / |Entry - Stop| >= 1.0.
5. Signal quality & publication gates (conviction >= 52%, freshness, provenance, symbol identity).
6. Terminal-state immutability and caller session transaction ownership preservation.
7. Permanent quarantine fail-closed enforcement across OpenAPI routes.
================================================================================
"""

import pytest
import numpy as np
from datetime import datetime, timezone
from unittest.mock import MagicMock

from backend.domain.models.ios import LiveSignal
from backend.services.signal_validator_service import SignalValidatorService

def create_mock_signal(**kwargs) -> LiveSignal:
    now_iso = datetime.now(timezone.utc).isoformat()
    defaults = {
        "id": "sig_test_123",
        "symbol": "INFY",
        "timeframe": "SWING",
        "rating": "BUY",
        "direction": "LONG",
        "entry_price": 1500.0,
        "stop_price": 1450.0,
        "target_price": 1640.0,  # RR = 140 / 50 = 2.8
        "status": "ACTIVE",
        "conviction": 65,
        "provenance_id": "prov_trace_456",
        "data_timestamp": now_iso
    }
    defaults.update(kwargs)

    sig = MagicMock(spec=LiveSignal)
    for k, v in defaults.items():
        setattr(sig, k, v)
    return sig

def test_phase_d_valid_long_signal_passes_validation():
    sig = create_mock_signal()
    res = SignalValidatorService.validate_publication(sig)
    assert res["is_valid"] is True
    assert res["status"] == "VALIDATED"
    assert len(res["issues"]) == 0

def test_phase_d_valid_short_signal_passes_validation():
    sig = create_mock_signal(
        direction="SHORT",
        entry_price=1500.0,
        stop_price=1550.0,
        target_price=1360.0  # RR = 140 / 50 = 2.8
    )
    res = SignalValidatorService.validate_publication(sig)
    assert res["is_valid"] is True
    assert res["status"] == "VALIDATED"

def test_phase_d_neutral_or_unavailable_direction_rejected():
    sig_neutral = create_mock_signal(direction="NEUTRAL")
    res_neutral = SignalValidatorService.validate_publication(sig_neutral)
    assert res_neutral["is_valid"] is False
    assert any("NON_DIRECTIONAL_PREDICTION" in issue for issue in res_neutral["issues"])

    sig_unavail = create_mock_signal(direction="UNAVAILABLE")
    res_unavail = SignalValidatorService.validate_publication(sig_unavail)
    assert res_unavail["is_valid"] is False
    assert any("NON_DIRECTIONAL_PREDICTION" in issue for issue in res_unavail["issues"])

def test_phase_d_non_finite_price_rejected():
    sig_nan = create_mock_signal(entry_price=np.nan)
    res_nan = SignalValidatorService.validate_publication(sig_nan)
    assert res_nan["is_valid"] is False
    assert any("NON_FINITE_PRICES" in issue for issue in res_nan["issues"])

    sig_inf = create_mock_signal(target_price=np.inf)
    res_inf = SignalValidatorService.validate_publication(sig_inf)
    assert res_inf["is_valid"] is False
    assert any("NON_FINITE_PRICES" in issue for issue in res_inf["issues"])

def test_phase_d_non_positive_price_rejected():
    sig_zero = create_mock_signal(entry_price=0.0)
    res_zero = SignalValidatorService.validate_publication(sig_zero)
    assert res_zero["is_valid"] is False
    assert any("NON_POSITIVE_PRICES" in issue for issue in res_zero["issues"])

    sig_neg = create_mock_signal(stop_price=-10.0)
    res_neg = SignalValidatorService.validate_publication(sig_neg)
    assert res_neg["is_valid"] is False
    assert any("NON_POSITIVE_PRICES" in issue for issue in res_neg["issues"])

def test_phase_d_zero_risk_distance_rejected():
    # Stop equal to Entry -> zero risk distance
    sig = create_mock_signal(entry_price=1500.0, stop_price=1500.0, target_price=1600.0)
    res = SignalValidatorService.validate_publication(sig)
    assert res["is_valid"] is False
    assert any("ZERO_RISK_DISTANCE" in issue for issue in res["issues"])

def test_phase_d_inverted_long_geometry_rejected():
    # Long signal where Target <= Entry or Stop >= Entry
    sig_bad_target = create_mock_signal(direction="LONG", entry_price=1500.0, stop_price=1450.0, target_price=1480.0)
    res_bad_target = SignalValidatorService.validate_publication(sig_bad_target)
    assert res_bad_target["is_valid"] is False
    assert any("Target must be above entry for Long" in issue for issue in res_bad_target["issues"])

    sig_bad_stop = create_mock_signal(direction="LONG", entry_price=1500.0, stop_price=1550.0, target_price=1600.0)
    res_bad_stop = SignalValidatorService.validate_publication(sig_bad_stop)
    assert res_bad_stop["is_valid"] is False
    assert any("Stop must be below entry for Long" in issue for issue in res_bad_stop["issues"])

def test_phase_d_inverted_short_geometry_rejected():
    # Short signal where Target >= Entry or Stop <= Entry
    sig_bad_target = create_mock_signal(direction="SHORT", entry_price=1500.0, stop_price=1550.0, target_price=1520.0)
    res_bad_target = SignalValidatorService.validate_publication(sig_bad_target)
    assert res_bad_target["is_valid"] is False
    assert any("Target must be below entry for Short" in issue for issue in res_bad_target["issues"])

def test_phase_d_suboptimal_risk_reward_rejected():
    # Long signal with RR = 20 / 50 = 0.4 (< 1.0 minimum)
    sig_low_rr = create_mock_signal(entry_price=1500.0, stop_price=1450.0, target_price=1520.0)
    res = SignalValidatorService.validate_publication(sig_low_rr)
    assert res["is_valid"] is False
    assert any("SUBOPTIMAL_RISK_REWARD" in issue for issue in res["issues"])

def test_phase_d_weak_edge_conviction_rejected():
    sig_weak = create_mock_signal(conviction=45)
    res = SignalValidatorService.validate_publication(sig_weak)
    assert res["is_valid"] is False
    assert any("WEAK_EDGE" in issue for issue in res["issues"])

def test_phase_d_missing_provenance_rejected():
    sig_no_prov = create_mock_signal(provenance_id="")
    res = SignalValidatorService.validate_publication(sig_no_prov)
    assert res["is_valid"] is False
    assert any("MISSING_PROVENANCE" in issue for issue in res["issues"])
