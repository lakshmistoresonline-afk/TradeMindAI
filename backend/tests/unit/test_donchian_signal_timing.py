import pandas as pd
import numpy as np
import pytest
from backend.app.services.indicator_service import LocalIndicatorService
from backend.app.services.signal_engine import SignalEngine

def make_sample_ohlcv(num_bars: int = 25, base_price: float = 100.0) -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=num_bars, freq="D")
    data = []
    for i, d in enumerate(dates):
        price = base_price + (i * 0.5)
        data.append({
            "timestamp": d,
            "open": price - 0.5,
            "high": price + 1.0,
            "low": price - 1.0,
            "close": price,
            "volume": 10000.0 + i * 100
        })
    df = pd.DataFrame(data)
    df.set_index("timestamp", inplace=True)
    return df

def test_donchian_shift_zero_lookahead_causality():
    # 25 bars. Bars 0..23 have high around 100..112.
    df = make_sample_ohlcv(25, 100.0)
    # Set bar 24 (last bar) high to extreme 500.0
    df.iloc[-1, df.columns.get_loc("high")] = 500.0

    df_ta = LocalIndicatorService.calculate_indicators(df)

    # The 20-period Donchian High for the last bar MUST NOT equal 500.0.
    # It must be equal to max(high) of bars 4..23 (prior 20 completed bars).
    prior_20_max = df["high"].iloc[-21:-1].max()
    latest_donchian = df_ta["donchian_high_20"].iloc[-1]

    assert latest_donchian == prior_20_max
    assert latest_donchian < 500.0, "Causality failure: current bar high contaminated Donchian boundary!"

def test_donchian_breakout_signal_generation():
    dates = pd.date_range("2026-01-01", periods=60, freq="D")
    data = []
    for i, d in enumerate(dates):
        p = 100.0 + (i % 3) * 0.5
        data.append({
            "timestamp": d,
            "open": p - 1.0,
            "high": p + 2.0,
            "low": p - 2.0,
            "close": p,
            "volume": 10000.0
        })
    df = pd.DataFrame(data)
    df.set_index("timestamp", inplace=True)

    prior_max_high = df["high"].iloc[-21:-1].max()

    # Set last bar high and close breaking out above prior max high
    df.iloc[-1, df.columns.get_loc("high")] = prior_max_high + 10.0
    df.iloc[-1, df.columns.get_loc("close")] = prior_max_high + 5.0

    signal = SignalEngine.generate_signal(df)
    assert signal["signal_type"] in ["BUY", "STRONG_BUY"]
    assert any("Donchian High" in d for d in signal["drivers"])

def test_forming_candle_high_does_not_shift_donchian_boundary():
    df = make_sample_ohlcv(25, 100.0)
    prior_max_high = df["high"].iloc[-21:-1].max()

    # Dynamic forming bar high changes from 120 to 300
    df.iloc[-1, df.columns.get_loc("high")] = 120.0
    metrics_1 = LocalIndicatorService.get_latest_metrics(df)

    df.iloc[-1, df.columns.get_loc("high")] = 300.0
    metrics_2 = LocalIndicatorService.get_latest_metrics(df)

    assert metrics_1["donchian_high_20"] == metrics_2["donchian_high_20"] == round(float(prior_max_high), 2)

def test_boundary_case_close_equals_donchian_high():
    df = make_sample_ohlcv(25, 100.0)
    prior_max_high = round(float(df["high"].iloc[-21:-1].max()), 2)

    df.iloc[-1, df.columns.get_loc("close")] = prior_max_high
    metrics = LocalIndicatorService.get_latest_metrics(df)

    assert metrics["donchian_high_20"] == prior_max_high
    assert metrics["close"] == prior_max_high

def test_insufficient_history_donchian_returns_none():
    df = make_sample_ohlcv(15, 100.0)
    metrics = LocalIndicatorService.get_latest_metrics(df)
    assert metrics.get("donchian_high_20") is None
    assert metrics.get("donchian_low_20") is None
