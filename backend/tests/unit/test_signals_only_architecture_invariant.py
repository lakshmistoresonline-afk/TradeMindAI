"""
================================================================================
TradeMindAI Phase 4.3.21: Dedicated Fifth Safety Invariant Adversarial Test Suite
================================================================================
Tests that all 5 runtime safety invariants are directly evaluated on settings object,
and that missing, non-boolean, or substitute variables fail closed immediately.
================================================================================
"""

import pytest
from unittest.mock import patch
from backend.core.config import settings
from backend.core.trading_safety import (
    trading_safety,
    TradingSafetyPolicy,
    TradingSafetyViolation,
    is_signals_only_architecture
)

def test_signals_only_architecture_positive_control():
    """Positive Control: All 5 safety flags correctly configured on settings evaluate True."""
    assert is_signals_only_architecture() is True
    assert getattr(settings, "REAL_TRADING", None) is False
    assert getattr(settings, "LIVE_EXECUTION_ENABLED", None) is False
    assert getattr(settings, "BROKER_ORDER_EXECUTION_ENABLED", None) is False
    assert getattr(settings, "QUARANTINE_ACTIVE", None) is True
    assert getattr(settings, "SIGNALS_ONLY_ARCHITECTURE", None) is True

def test_signals_only_architecture_fifth_setting_absent_fails_closed():
    """
    Critical Adversarial Test:
    When SIGNALS_ONLY_ARCHITECTURE is absent from settings (returns None),
    even if trading_safety.real_trading_enabled == False,
    is_signals_only_architecture() MUST fail closed (return False).
    Proves fifth invariant cannot be bypassed by substitute variables!
    """
    with patch.object(settings, "SIGNALS_ONLY_ARCHITECTURE", None, create=True):
        assert is_signals_only_architecture() is False

def test_signals_only_architecture_fifth_setting_false_fails_closed():
    """Negative Control: When SIGNALS_ONLY_ARCHITECTURE is False, is_signals_only_architecture() returns False."""
    with patch.object(settings, "SIGNALS_ONLY_ARCHITECTURE", False):
        assert is_signals_only_architecture() is False

def test_signals_only_architecture_non_boolean_fails_closed():
    """Negative Control: String 'true' or integer 1 fails strict boolean identity check."""
    with patch.object(settings, "SIGNALS_ONLY_ARCHITECTURE", "true"):
        assert is_signals_only_architecture() is False

    with patch.object(settings, "SIGNALS_ONLY_ARCHITECTURE", 1):
        assert is_signals_only_architecture() is False

def test_signals_only_architecture_first_four_flags_fails_closed():
    """Negative Control: Reversing any of the first four safety flags fails closed immediately."""
    with patch.object(settings, "REAL_TRADING", True):
        assert is_signals_only_architecture() is False

    with patch.object(settings, "LIVE_EXECUTION_ENABLED", True):
        assert is_signals_only_architecture() is False

    with patch.object(settings, "BROKER_ORDER_EXECUTION_ENABLED", True):
        assert is_signals_only_architecture() is False

    with patch.object(settings, "QUARANTINE_ACTIVE", False):
        assert is_signals_only_architecture() is False
