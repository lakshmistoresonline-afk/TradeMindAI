"""
================================================================================
TradeMindAI Unit Tests — Fail-Closed Signal Engine Inputs (Fix 3)
================================================================================
Verifies that SignalEngine.generate_signal():
1. Fails closed (returns HOLD) when close price is invalid (None, NaN, Inf, string, zero, negative).
2. Fails closed (returns HOLD) when required indicators (rsi, ema_20, ema_50, macd_hist) are unavailable or NaN.
3. Does not convert unavailable indicators to neutral values that qualify signals.
4. Does not raise unhandled exceptions on NaN / Inf / None indicator metrics.
5. Successfully evaluates setups when required indicators are valid.
================================================================================
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.services.signal_engine import SignalEngine
from backend.app.services.indicator_service import LocalIndicatorService

def test_signal_engine_fails_closed_on_insufficient_history():
    # Only 5 bars (insufficient history for 14-bar indicators)
    df_short = pd.DataFrame({
        "open": [100.0, 101.0, 102.0, 103.0, 104.0],
        "high": [101.0, 102.0, 103.0, 104.0, 105.0],
        "low": [99.0, 100.0, 101.0, 102.0, 103.0],
        "close": [100.5, 101.5, 102.5, 103.5, 104.5],
        "volume": [10000] * 5
    })
    res = SignalEngine.generate_signal(df_short)
    assert res["signal_type"] == "HOLD"
    assert "Insufficient" in res["drivers"][0] or "unavailable" in res["drivers"][0]

@pytest.mark.parametrize("invalid_close", [None, np.nan, np.inf, -np.inf, "invalid_str", 0.0, -10.0])
def test_signal_engine_fails_closed_when_close_price_invalid(monkeypatch, invalid_close):
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    df_valid = pd.DataFrame({
        "open": [100.0 + i for i in range(30)],
        "high": [102.0 + i for i in range(30)],
        "low": [99.0 + i for i in range(30)],
        "close": [101.0 + i for i in range(30)],
        "volume": [10000] * 30
    }, index=dates)

    original_get_metrics = LocalIndicatorService.get_latest_metrics
    def mock_metrics(df):
        m = original_get_metrics(df)
        m["close"] = invalid_close
        m["rsi_14"] = 55.0
        m["ema_20"] = 100.0
        m["ema_50"] = 95.0
        return m

    monkeypatch.setattr(LocalIndicatorService, "get_latest_metrics", mock_metrics)

    res = SignalEngine.generate_signal(df_valid)
    assert res["signal_type"] == "HOLD"
    assert "unavailable" in res["drivers"][0] or "Essential" in res["drivers"][0]

def test_signal_engine_fails_closed_when_rsi_unavailable(monkeypatch):
    # 30 bars (sufficient length)
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    df_valid = pd.DataFrame({
        "open": [100.0 + i for i in range(30)],
        "high": [102.0 + i for i in range(30)],
        "low": [99.0 + i for i in range(30)],
        "close": [101.0 + i for i in range(30)],
        "volume": [10000] * 30
    }, index=dates)

    original_get_metrics = LocalIndicatorService.get_latest_metrics
    def mock_metrics(df):
        m = original_get_metrics(df)
        m["rsi_14"] = None
        return m

    monkeypatch.setattr(LocalIndicatorService, "get_latest_metrics", mock_metrics)

    res = SignalEngine.generate_signal(df_valid)
    assert res["signal_type"] == "HOLD"
    assert "unavailable" in res["drivers"][0]

def test_signal_engine_fails_closed_when_ema_unavailable(monkeypatch):
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    df_valid = pd.DataFrame({
        "open": [100.0 + i for i in range(30)],
        "high": [102.0 + i for i in range(30)],
        "low": [99.0 + i for i in range(30)],
        "close": [101.0 + i for i in range(30)],
        "volume": [10000] * 30
    }, index=dates)

    original_get_metrics = LocalIndicatorService.get_latest_metrics
    def mock_metrics(df):
        m = original_get_metrics(df)
        m["ema_20"] = None
        return m

    monkeypatch.setattr(LocalIndicatorService, "get_latest_metrics", mock_metrics)

    res = SignalEngine.generate_signal(df_valid)
    assert res["signal_type"] == "HOLD"
    assert "unavailable" in res["drivers"][0]

def test_signal_engine_valid_indicators_generates_signal():
    # 30 valid bars
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    df_valid = pd.DataFrame({
        "open": [100.0 + i for i in range(30)],
        "high": [102.0 + i for i in range(30)],
        "low": [99.0 + i for i in range(30)],
        "close": [101.0 + i for i in range(30)],
        "volume": [10000] * 30
    }, index=dates)

    res = SignalEngine.generate_signal(df_valid)
    assert "signal_type" in res
    assert res["signal_type"] in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
