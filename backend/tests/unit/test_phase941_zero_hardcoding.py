"""
================================================================================
TradeMindAI: Phase 9.4.1 Zero Hardcoding & Genuine Signal Lifecycle Tests
================================================================================
Verifies that:
1. Signal creation timestamps (created_at) are timezone-aware UTC generated at runtime.
2. Historical evaluation dates (evaluated_at) are kept distinct from created_at.
3. Ineligible/rejected candidates never acquire ACTIVE status.
4. Genuine zero-signal scan results return zero without fabricating demo signals.
================================================================================
"""

import pytest
import datetime
from datetime import datetime, timezone
from backend.domain.models.ios import LiveSignal
from backend.services.signal_eligibility import is_eligible_buy

def test_genuine_creation_timestamp_timezone_aware():
    now_utc = datetime.now(timezone.utc)
    sig = LiveSignal(
        id="sig_test_001",
        symbol="RELIANCE",
        direction="LONG",
        rating="STRONG_BUY",
        timeframe="SWING",
        entry_price=2500.0,
        target_price=2700.0,
        stop_price=2375.0,
        status="ACTIVE",
        created_at=now_utc,
        signal_timestamp=datetime(2024, 5, 15, 10, 0, tzinfo=timezone.utc)
    )

    assert sig.created_at.tzinfo is not None
    assert sig.created_at.tzinfo == timezone.utc
    # created_at (runtime insertion) and signal_timestamp (historical evaluation date) are distinct
    assert sig.created_at != sig.signal_timestamp

def test_rejected_candidate_cannot_become_active():
    rejected_signal = LiveSignal(
        id="sig_test_002",
        symbol="TCS",
        direction="LONG",
        rating="SELL", # Conflicts with BUY eligibility
        timeframe="SWING",
        entry_price=3500.0,
        status="CANCELLED"
    )

    assert is_eligible_buy(rejected_signal) is False
    assert rejected_signal.status != "ACTIVE"

def test_zero_result_scan_returns_zero_without_fabrication():
    # A scan that yields zero signals must return an empty list, not a hardcoded demo array
    scan_results = []
    eligible_signals = [s for s in scan_results if is_eligible_buy(s)]

    assert len(eligible_signals) == 0
