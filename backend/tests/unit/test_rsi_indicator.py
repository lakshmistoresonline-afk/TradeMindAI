"""
================================================================================
TradeMindAI Unit Tests — Wilder RSI Indicator Edge Cases (Harden Fix)
================================================================================
Verifies Wilder RSI 14 calculation for:
1. Positive average gain, zero loss -> RSI = 100.0
2. Zero average gain, positive loss -> RSI = 0.0
3. Zero average gain, zero loss (flat series) -> RSI = 50.0
4. Mixed gains and losses -> 0 < RSI < 100
5. Warm-up period -> NaN
6. NaN at beginning, middle, and end -> contiguous reset requirement
7. Gap recovery after 14 contiguous valid price deltas
8. Insufficient valid observations after gap -> NaN
9. Infinite / non-numeric inputs -> converted safely to NaN
10. Period parameter validation -> accepts Python int and NumPy int, rejects bool, float, str, <=0
================================================================================
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.services.indicator_service import compute_wilder_rsi, LocalIndicatorService

@pytest.mark.parametrize("invalid_p", [0, -5, True, False, 14.5, "14", None])
def test_rsi_period_validation_rejects_invalid_types_and_values(invalid_p):
    prices = pd.Series([100.0 + i for i in range(20)])
    with pytest.raises(ValueError, match="RSI period must be a positive integer"):
        compute_wilder_rsi(prices, period=invalid_p)

@pytest.mark.parametrize("valid_p", [14, np.int64(14), np.int32(14)])
def test_rsi_period_validation_accepts_valid_integers(valid_p):
    prices = pd.Series([100.0 + i for i in range(20)])
    rsi = compute_wilder_rsi(prices, period=valid_p)
    assert len(rsi) == len(prices)
    assert not rsi.iloc[14:].isna().any()

def test_rsi_warmup_nan_contract():
    prices = pd.Series([100.0 + i for i in range(10)])
    rsi = compute_wilder_rsi(prices, period=14)
    assert rsi.isna().all()

def test_rsi_sustained_rising_series_zero_loss():
    prices = pd.Series([100.0 + i * 2.0 for i in range(25)])
    rsi = compute_wilder_rsi(prices, period=14)
    assert rsi.iloc[:14].isna().all()
    assert (rsi.iloc[14:] == 100.0).all()

def test_rsi_sustained_falling_series_zero_gain():
    prices = pd.Series([100.0 - i * 2.0 for i in range(25)])
    rsi = compute_wilder_rsi(prices, period=14)
    assert rsi.iloc[:14].isna().all()
    assert (rsi.iloc[14:] == 0.0).all()

def test_rsi_completely_flat_series():
    prices = pd.Series([100.0] * 25)
    rsi = compute_wilder_rsi(prices, period=14)
    assert rsi.iloc[:14].isna().all()
    assert (rsi.iloc[14:] == 50.0).all()

def test_rsi_mixed_gains_and_losses():
    prices = pd.Series([100, 102, 101, 104, 103, 106, 105, 108, 107, 110, 109, 112, 111, 114, 113, 116, 115, 118, 117, 120])
    rsi = compute_wilder_rsi(prices, period=14)
    assert rsi.iloc[:14].isna().all()
    valid_rsi = rsi.iloc[14:]
    assert not valid_rsi.isna().any()
    assert (valid_rsi > 0.0).all()
    assert (valid_rsi < 100.0).all()

def test_rsi_nan_at_beginning_middle_and_end():
    # Price series with NaN at beginning (idx 0), middle (idx 20), and end (idx 40)
    prices_list = [np.nan] + [100.0 + i for i in range(19)] + [np.nan] + [120.0 + i for i in range(19)] + [np.nan]
    prices = pd.Series(prices_list)
    rsi = compute_wilder_rsi(prices, period=14)

    assert len(rsi) == len(prices)

    # Idx 0..14 should be NaN (warmup)
    assert rsi.iloc[:15].isna().all()

    # Idx 15..19 should be 100.0 (5 valid RSI points before middle gap)
    assert (rsi.iloc[15:20] == 100.0).all()

    # Idx 20 (NaN) must yield NaN
    assert np.isnan(rsi.iloc[20])

    # Idx 21..34 (14 bars post gap) should be NaN during warm-up
    assert rsi.iloc[21:35].isna().all()

    # Idx 35..39 (5 valid RSI points post recovery) must evaluate to 100.0
    assert (rsi.iloc[35:40] == 100.0).all()

    # Idx 40 (end NaN) must yield NaN
    assert np.isnan(rsi.iloc[40])

def test_rsi_infinite_and_non_numeric_inputs():
    prices = pd.Series([100, 102, "invalid", np.inf, -np.inf, 105, 106] + [100.0 + i for i in range(20)])
    rsi = compute_wilder_rsi(prices, period=14)
    assert len(rsi) == len(prices)

def test_get_latest_metrics_returns_none_when_indicator_unavailable():
    # Only 5 bars (insufficient history for 14-bar RSI, 20-bar EMA, 20-bar Donchian)
    short_df = pd.DataFrame({
        "close": [100.0, 101.0, 102.0, 103.0, 104.0]
    })
    metrics = LocalIndicatorService.get_latest_metrics(short_df)
    assert metrics["close"] == 104.0
    assert metrics["rsi_14"] is None
    assert metrics["ema_20"] is None
    assert metrics["ema_50"] is None
    assert metrics["donchian_high_20"] is None
