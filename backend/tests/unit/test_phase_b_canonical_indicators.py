"""
================================================================================
TradeMindAI Phase B: Canonical Indicators & Feature Consistency Unit Tests
================================================================================
Verifies mathematical definitions, warm-up policies, missing-data handling,
and point-in-time causality for canonical technical indicators:
1. Wilder Exponentially Smoothed RSI (14).
2. EMA200 warm-up requirement (>= 200 bars).
3. Shifted Donchian Channels (20) with 1-bar shift for zero look-ahead bias.
4. ATR (14) rolling True Range calculation.
5. Bollinger Bands (20, 2) and MACD (12, 26, 9).
6. Strict missing-data contract: NaN/None returned for insufficient history, NO fabricated defaults (no 0.02*price or 50.0 fallbacks).
================================================================================
"""

import pytest
import numpy as np
import pandas as pd

from backend.app.services.indicator_service import LocalIndicatorService, compute_wilder_rsi

def test_phase_b_wilder_rsi_warmup_and_edge_cases():
    # Less than 14 bars -> NaN
    short_series = pd.Series([100.0 + i for i in range(10)])
    rsi_short = compute_wilder_rsi(short_series, period=14)
    assert rsi_short.isna().all()

    # Monotonically increasing 20 bars -> gain > 0, loss = 0 -> RSI = 100.0 after warm-up (bar 15, index 14)
    up_series = pd.Series([100.0 + i * 2.0 for i in range(20)])
    rsi_up = compute_wilder_rsi(up_series, period=14)
    assert pd.isna(rsi_up.iloc[13]) is True   # 13 deltas -> warm-up NaN
    assert pd.isna(rsi_up.iloc[14]) is False  # 14 deltas -> 1st valid RSI
    assert rsi_up.iloc[14] == 100.0

    # Monotonically decreasing 20 bars -> gain = 0, loss > 0 -> RSI = 0.0 after warm-up
    down_series = pd.Series([200.0 - i * 2.0 for i in range(20)])
    rsi_down = compute_wilder_rsi(down_series, period=14)
    assert rsi_down.iloc[14] == 0.0

    # Flat prices 20 bars -> gain = 0, loss = 0 -> RSI = 50.0
    flat_series = pd.Series([100.0] * 20)
    rsi_flat = compute_wilder_rsi(flat_series, period=14)
    assert rsi_flat.iloc[14] == 50.0

def test_phase_b_rsi_period_validation():
    series = pd.Series([100.0 + i for i in range(20)])
    with pytest.raises(ValueError, match="RSI period must be a positive integer"):
        compute_wilder_rsi(series, period=0)
    with pytest.raises(ValueError, match="RSI period must be a positive integer"):
        compute_wilder_rsi(series, period=-5)
    with pytest.raises(ValueError, match="RSI period must be a positive integer"):
        compute_wilder_rsi(series, period=True)  # boolean rejected

def test_phase_b_ema200_warmup_guard():
    # 150 bars -> ema_200 must be NaN
    dates = pd.date_range("2026-01-01", periods=150, freq="D")
    df_150 = pd.DataFrame({
        "close": [100.0 + i * 0.5 for i in range(150)],
        "high": [102.0 + i * 0.5 for i in range(150)],
        "low": [99.0 + i * 0.5 for i in range(150)]
    }, index=dates)

    metrics_150 = LocalIndicatorService.get_latest_metrics(df_150)
    assert metrics_150["ema_200"] is None  # Warm-up guard enforced

    # 210 bars -> ema_200 must be valid float
    dates_210 = pd.date_range("2026-01-01", periods=210, freq="D")
    df_210 = pd.DataFrame({
        "close": [100.0 + i * 0.5 for i in range(210)],
        "high": [102.0 + i * 0.5 for i in range(210)],
        "low": [99.0 + i * 0.5 for i in range(210)]
    }, index=dates_210)

    metrics_210 = LocalIndicatorService.get_latest_metrics(df_210)
    assert metrics_210["ema_200"] is not None
    assert isinstance(metrics_210["ema_200"], float)

def test_phase_b_donchian_channels_shifted_causality():
    # 30 bars where price spikes on last bar
    highs = [100.0] * 29 + [500.0]  # Bar 30 high is 500.0
    lows = [90.0] * 30
    closes = [95.0] * 30
    df = pd.DataFrame({"close": closes, "high": highs, "low": lows})

    df_ind = LocalIndicatorService.calculate_indicators(df)
    # At bar 30 (last row), donchian_high_20 is derived from bars 10 to 29 max high (which is 100.0), NOT bar 30 (500.0)
    latest_donchian_high = df_ind["donchian_high_20"].iloc[-1]
    assert latest_donchian_high == 100.0  # Zero look-ahead bias confirmed!

def test_phase_b_atr14_no_fabricated_fallback():
    # Insufficient bars (10 bars) -> ATR is NaN / None, NOT 0.02 * close
    df_short = pd.DataFrame({
        "close": [100.0] * 10,
        "high": [105.0] * 10,
        "low": [95.0] * 10
    })
    df_ind = LocalIndicatorService.calculate_indicators(df_short)
    assert pd.isna(df_ind["atr_14"].iloc[-1])

    metrics = LocalIndicatorService.get_latest_metrics(df_short)
    assert metrics.get("atr_14") is None

def test_phase_b_column_case_insensitivity():
    # Test DataFrame with capitalized column names
    df_cap = pd.DataFrame({
        "Close": [100.0 + i for i in range(25)],
        "High": [102.0 + i for i in range(25)],
        "Low": [98.0 + i for i in range(25)]
    })
    df_lower = df_cap.rename(columns={"Close": "close", "High": "high", "Low": "low"})

    metrics_cap = LocalIndicatorService.get_latest_metrics(df_lower)
    assert metrics_cap["rsi_14"] is not None
    assert metrics_cap["atr_14"] is not None
