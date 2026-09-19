import pytest
import pandas as pd
import datetime
from backend.services.outcome_service import OutcomeService
from backend.domain.models.ios import LiveSignal

def test_same_bar_ambiguity():
    """
    P0: Proving the system detects AMBIGUOUS when both target and stop are hit in one bar.
    """
    signal = LiveSignal(
        id="test_sig",
        symbol="RELIANCE",
        direction="LONG",
        entry_price=2500.0,
        target_price=2600.0,
        stop_price=2400.0,
        timestamp=datetime.datetime(2026, 9, 18, 10, 0),
        status="ACTIVE"
    )

    # Bar that hits both
    df = pd.DataFrame([
        {"Open": 2510.0, "High": 2650.0, "Low": 2350.0, "Close": 2550.0, "Volume": 100}
    ], index=[datetime.datetime(2026, 9, 18, 11, 0)])

    res = OutcomeService.evaluate_signal_outcome(signal, df)

    assert res["status"] == "AMBIGUOUS"
    assert res["exit_reason"] == "SAME_BAR_AMBIGUITY"
    assert res["exit_price"] is None

def test_sequential_hit_stop_first():
    """Verify standard stop loss hit."""
    signal = LiveSignal(
        id="test_sig", symbol="RELIANCE", direction="LONG",
        entry_price=2500.0, target_price=2600.0, stop_price=2400.0,
        timestamp=datetime.datetime(2026, 9, 18, 10, 0), status="ACTIVE"
    )

    df = pd.DataFrame([
        {"Open": 2510.0, "High": 2550.0, "Low": 2350.0, "Close": 2450.0}
    ], index=[datetime.datetime(2026, 9, 18, 11, 0)])

    res = OutcomeService.evaluate_signal_outcome(signal, df)
    assert res["status"] == "STOP_LOSS"

if __name__ == "__main__":
    pytest.main([__file__])
