import pytest
import pandas as pd
import numpy as np
from backend.analysis.research_features import ResearchFeatures
from backend.analysis.research_scorer import ResearchScorer
from backend.analysis.smc import SMCAnalysis

def test_research_features_ohlcv_validation_robust():
    # Test lowercase columns, normalization, and no mutation of original df
    df_raw = pd.DataFrame({
        "open": [100, 101, 102, 103, 104],
        "high": [102, 103, 104, 105, 106],
        "low": [99, 100, 101, 102, 103],
        "close": [101, 102, 103, 104, 105],
        "volume": [1000, 1100, 1200, 1300, 1400]
    }, index=pd.date_range("2026-01-01", periods=5))

    df_clean = ResearchFeatures.validate_ohlcv(df_raw)
    assert "Open" in df_clean.columns
    assert "open" in df_raw.columns  # original not mutated

    # Test duplicate columns rejection after normalization
    df_dup = pd.DataFrame({
        "Open": [100, 101],
        "High": [102, 103],
        "Low": [99, 100],
        "Close": [101, 102],
        "Volume": [1000, 1100],
        "open": [100, 101]
    }, index=pd.date_range("2026-01-01", periods=2))
    with pytest.raises(ValueError, match="Duplicate columns"):
        ResearchFeatures.validate_ohlcv(df_dup)

    # Test non-monotonic index rejection
    df_bad_idx = pd.DataFrame({
        "Open": [100, 101],
        "High": [102, 103],
        "Low": [99, 100],
        "Close": [101, 102],
        "Volume": [1000, 1100]
    }, index=[pd.Timestamp("2026-01-02"), pd.Timestamp("2026-01-01")])
    with pytest.raises(ValueError, match="not monotonically increasing"):
        ResearchFeatures.validate_ohlcv(df_bad_idx)

def test_benchmark_normalization_and_alignment():
    dates = pd.date_range("2026-01-01", periods=60, freq="B")
    df = pd.DataFrame({
        "Open": [100]*60, "High": [105]*60, "Low": [95]*60, "Close": [102]*60, "Volume": [1000]*60
    }, index=dates)

    # Test benchmark with lowercase columns covering full OHLCV
    bench_lower = pd.DataFrame({
        "open": [1000]*60, "high": [1050]*60, "low": [950]*60, "close": [1020]*60, "volume": [10000]*60
    }, index=dates)

    res_df = ResearchFeatures.calculate_research_features(df, benchmark_df=bench_lower)
    assert "res_rs_20d" in res_df.columns
    assert not res_df["res_rs_20d"].isna().all()

    # Test missing benchmark returns NaN without error
    res_no_bench = ResearchFeatures.calculate_research_features(df, benchmark_df=None)
    assert res_no_bench["res_rs_20d"].isna().all()

def test_donchian_shift_causality():
    dates = pd.date_range(end=pd.Timestamp.today(), periods=70, freq="B")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(70) * 1.0)
    high = close + 2.0
    low = close - 2.0
    df = pd.DataFrame({
        "Open": close,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": 100000.0
    }, index=dates)

    # Spike the current candle high on the last row
    df.iloc[-1, df.columns.get_loc("High")] = 200.0
    df.iloc[-1, df.columns.get_loc("Close")] = 195.0

    res_df = ResearchFeatures.calculate_research_features(df)
    rolling_max_prior = df["High"].iloc[-21:-1].max()
    assert res_df["res_donchian_high_20"].iloc[-1] == rolling_max_prior
    assert res_df["res_donchian_high_20"].iloc[-1] < 200.0

def test_full_feature_mutation_invariance():
    dates = pd.date_range(end=pd.Timestamp.today(), periods=70, freq="B")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(70) * 1.0)
    df = pd.DataFrame({
        "Open": close,
        "High": close + 2.0,
        "Low": close - 2.0,
        "Close": close,
        "Volume": 100000.0
    }, index=dates)

    df_prefix = df.iloc[:60].copy()
    res_prefix = ResearchFeatures.calculate_research_features(df_prefix)

    df_full = df.copy()
    df_full.iloc[60:, df_full.columns.get_loc("Close")] += 10.0
    df_full.iloc[60:, df_full.columns.get_loc("Open")] += 10.0
    df_full.iloc[60:, df_full.columns.get_loc("High")] += 12.0
    df_full.iloc[60:, df_full.columns.get_loc("Low")] += 8.0

    res_full = ResearchFeatures.calculate_research_features(df_full)

    res_cols = [c for c in res_prefix.columns if c.startswith("res_") or c in ["ema_20", "ema_50", "momentum_rsi"]]
    for col in res_cols:
        assert np.allclose(res_prefix[col].iloc[:55], res_full[col].iloc[:55], equal_nan=True)

def test_research_scorer_numeric_domains_and_policy_a():
    base_row = {
        "Close": 110.0, "ema_20": 105.0, "ema_50": 100.0, "ema_200": 90.0,
        "res_ema_slope_5": 0.1, "momentum_rsi": 55.0, "res_adx_14": 22.0,
        "res_rel_vol_20": 1.2, "res_mfi_14": 60.0, "res_natr": 2.0,
        "res_rs_20d": 0.05, "res_donchian_high_20": 108.0
    }

    res_valid = ResearchScorer.evaluate_research_signal(pd.Series(base_row))
    assert res_valid["status"] == "AVAILABLE"
    assert res_valid["calibrated_probability"] is None

    # Test invalid domain values and types (booleans, strings, out-of-bounds RSI, negative price)
    invalid_cases = [
        ("ema_20", None),
        ("momentum_rsi", np.nan),
        ("momentum_rsi", 150.0),  # out of [0, 100]
        ("Close", -10.0),  # non-positive price
        ("res_natr", float("inf")),
        ("res_rel_vol_20", "string_val"),
        ("res_adx_14", True),  # boolean rejected
        ("res_donchian_high_20", np.bool_(False))  # numpy boolean rejected
    ]

    for key, bad_val in invalid_cases:
        row_dict = base_row.copy()
        row_dict[key] = bad_val
        res_bad = ResearchScorer.evaluate_research_signal(pd.Series(row_dict))
        assert res_bad["status"] == "UNAVAILABLE", f"Failed to reject {key} = {bad_val}"
        assert res_bad["composite_score"] is None

def test_smc_fvg_and_ob_causality():
    df = pd.DataFrame({
        "Open": [100, 102, 101, 105],
        "High": [101, 103, 102, 108],
        "Low": [99, 101, 100, 104],
        "Close": [100.5, 102.5, 101.5, 107],
        "Volume": [1000, 1000, 1000, 5000]
    }, index=pd.date_range("2026-01-01", periods=4))

    fvgs = SMCAnalysis.detect_fvg(df)
    for fvg in fvgs:
        assert fvg["pattern_index"] >= 1
        assert fvg["confirmation_index"] == fvg["pattern_index"] + 1
        assert fvg["confirmation_timestamp"] == df.index[fvg["confirmation_index"]]

    obs = SMCAnalysis.detect_order_blocks(df)
    for ob in obs:
        assert ob["zone_index"] >= 0
        assert ob["confirmation_index"] >= 0
        assert ob["confirmation_timestamp"] == df.index[ob["confirmation_index"]]
