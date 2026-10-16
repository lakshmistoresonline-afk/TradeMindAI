import pytest
import pandas as pd
import numpy as np
from backend.analysis.smc import SMCAnalysis

def test_smc_input_validation_and_errors():
    # 1. Invalid columns
    df_bad_cols = pd.DataFrame({
        "A": [100.0, 101.0, 102.0],
        "B": [101.0, 102.0, 103.0]
    }, index=pd.date_range("2026-01-01", periods=3))
    with pytest.raises(ValueError, match="Missing required column"):
        SMCAnalysis.detect_fvg(df_bad_cols)

    # 2. Duplicate normalized columns collision (e.g. Close and close)
    df_dup_norm = pd.DataFrame({
        "Open": [100.0, 101.0, 102.0],
        "High": [102.0, 103.0, 104.0],
        "Low": [99.0, 100.0, 101.0],
        "Close": [101.0, 102.0, 103.0],
        " close ": [101.0, 102.0, 103.0]
    }, index=pd.date_range("2026-01-01", periods=3))
    with pytest.raises(ValueError, match="Duplicate columns detected"):
        SMCAnalysis.detect_order_blocks(df_dup_norm)

    # 3. Non-finite values
    df_nan = pd.DataFrame({
        "Open": [100.0, 101.0, np.nan],
        "High": [102.0, 103.0, 104.0],
        "Low": [99.0, 100.0, 101.0],
        "Close": [101.0, 102.0, 103.0]
    }, index=pd.date_range("2026-01-01", periods=3))
    with pytest.raises(ValueError, match="non-finite or non-numeric"):
        SMCAnalysis.detect_order_blocks(df_nan)

    # 4. Duplicate timestamps
    df_dup_ts = pd.DataFrame({
        "Open": [100.0, 101.0, 102.0],
        "High": [102.0, 103.0, 104.0],
        "Low": [99.0, 100.0, 101.0],
        "Close": [101.0, 102.0, 103.0]
    }, index=[pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-02")])
    with pytest.raises(ValueError, match="Duplicate timestamps"):
        SMCAnalysis.detect_fvg(df_dup_ts)

    # 5. Unordered timestamps
    df_unordered = pd.DataFrame({
        "Open": [100.0, 101.0, 102.0],
        "High": [102.0, 103.0, 104.0],
        "Low": [99.0, 100.0, 101.0],
        "Close": [101.0, 102.0, 103.0]
    }, index=[pd.Timestamp("2026-01-02"), pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-03")])
    with pytest.raises(ValueError, match="not monotonically increasing"):
        SMCAnalysis.detect_fvg(df_unordered)

def test_smc_no_patterns_empty_list():
    df_flat = pd.DataFrame({
        "Open": [100.0]*15,
        "High": [102.0]*15,
        "Low": [98.0]*15,
        "Close": [100.0]*15
    }, index=pd.date_range("2026-01-01", periods=15))

    assert SMCAnalysis.detect_fvg(df_flat) == []
    assert SMCAnalysis.detect_order_blocks(df_flat) == []

def test_detect_fvg_exact_outcomes():
    dates = pd.date_range("2026-01-01", periods=3)
    df = pd.DataFrame({
        "Open": [100.0, 102.0, 106.0],
        "High": [101.0, 103.0, 110.0],
        "Low": [99.0, 101.0, 105.0],
        "Close": [100.5, 102.5, 108.0]
    }, index=dates, dtype=float)

    fvgs = SMCAnalysis.detect_fvg(df)
    assert len(fvgs) == 1
    assert fvgs[0]["type"] == "bullish"
    assert fvgs[0]["bottom"] == 101.0
    assert fvgs[0]["top"] == 105.0
    assert fvgs[0]["pattern_index"] == 1
    assert fvgs[0]["confirmation_index"] == 2
    assert fvgs[0]["confirmation_timestamp"] == dates[2]

def test_detect_bullish_order_block_exact_outcomes():
    dates = pd.date_range("2026-01-01", periods=10)
    df = pd.DataFrame({
        "Open": [100.0]*10,
        "High": [102.0]*10,
        "Low": [98.0]*10,
        "Close": [100.0]*10
    }, index=dates, dtype=float)

    # Bullish OB at index 2 (down candle Open 105, Close 100, Low 97, High 106)
    df.iloc[2, df.columns.get_loc("Open")] = 105.0
    df.iloc[2, df.columns.get_loc("Close")] = 100.0
    df.iloc[2, df.columns.get_loc("Low")] = 97.0
    df.iloc[2, df.columns.get_loc("High")] = 106.0

    # Displacement up at index 3 (Close 115 > High 106 * 1.01 = 107.06)
    df.iloc[3, df.columns.get_loc("Open")] = 101.0
    df.iloc[3, df.columns.get_loc("Close")] = 115.0
    df.iloc[3, df.columns.get_loc("High")] = 116.0
    df.iloc[3, df.columns.get_loc("Low")] = 99.0

    obs = SMCAnalysis.detect_order_blocks(df)
    bullish_obs = [o for o in obs if o["type"] == "bullish"]
    assert len(bullish_obs) == 1
    ob = bullish_obs[0]
    assert ob["zone_index"] == 2
    assert ob["confirmation_index"] == 3
    assert ob["price"] == 97.0
    assert ob["confirmation_timestamp"] == dates[3]

def test_detect_bearish_order_block_exact_outcomes():
    dates = pd.date_range("2026-01-01", periods=10)
    df = pd.DataFrame({
        "Open": [100.0]*10,
        "High": [102.0]*10,
        "Low": [98.0]*10,
        "Close": [100.0]*10
    }, index=dates, dtype=float)

    # Bearish OB: Up candle at index 2 (Open 100, Close 105, Low 99, High 106)
    df.iloc[2, df.columns.get_loc("Open")] = 100.0
    df.iloc[2, df.columns.get_loc("Close")] = 105.0
    df.iloc[2, df.columns.get_loc("Low")] = 99.0
    df.iloc[2, df.columns.get_loc("High")] = 106.0

    # Displacement down at index 3 (Close 90 < Low 98 * 0.99 = 97.02)
    df.iloc[3, df.columns.get_loc("Open")] = 101.0
    df.iloc[3, df.columns.get_loc("Close")] = 90.0
    df.iloc[3, df.columns.get_loc("High")] = 102.0
    df.iloc[3, df.columns.get_loc("Low")] = 89.0

    obs = SMCAnalysis.detect_order_blocks(df)
    bearish_obs = [o for o in obs if o["type"] == "bearish"]
    assert len(bearish_obs) == 1
    ob_bear = bearish_obs[0]
    assert ob_bear["zone_index"] == 2
    assert ob_bear["confirmation_index"] == 3
    assert ob_bear["price"] == 106.0
    assert ob_bear["confirmation_timestamp"] == dates[3]

def test_order_block_threshold_boundary():
    dates = pd.date_range("2026-01-01", periods=10)
    # Test strict threshold: 1.01x High
    # If High[2] is 100.0 (down candle Open 102, Close 100, High 102), threshold is 102.0 * 1.01 = 103.02.
    df = pd.DataFrame({
        "Open": [100.0]*10, "High": [102.0]*10, "Low": [98.0]*10, "Close": [100.0]*10
    }, index=dates, dtype=float)
    df.iloc[2, df.columns.get_loc("Open")] = 102.0
    df.iloc[2, df.columns.get_loc("Close")] = 100.0
    df.iloc[2, df.columns.get_loc("Low")] = 97.0
    df.iloc[2, df.columns.get_loc("High")] = 102.0

    # Case A: Close[3] = 103.0 (below 102.0 * 1.01 = 103.02) -> No OB
    df.iloc[3, df.columns.get_loc("Close")] = 103.0
    df.iloc[3, df.columns.get_loc("High")] = 104.0
    df.iloc[3, df.columns.get_loc("Open")] = 100.0
    df.iloc[3, df.columns.get_loc("Low")] = 99.0
    assert SMCAnalysis.detect_order_blocks(df) == []

    # Case B: Close[3] = 103.03 (above 103.02) -> OB detected
    df.iloc[3, df.columns.get_loc("Close")] = 103.03
    df.iloc[3, df.columns.get_loc("High")] = 104.0
    df.iloc[3, df.columns.get_loc("Open")] = 100.0
    df.iloc[3, df.columns.get_loc("Low")] = 99.0
    obs = SMCAnalysis.detect_order_blocks(df)
    assert len(obs) == 1

def test_displacement_at_final_row():
    # Verify order block confirmation can occur at the final row of the series
    dates = pd.date_range("2026-01-01", periods=4)
    df = pd.DataFrame({
        "Open": [100.0, 100.0, 105.0, 101.0],
        "High": [102.0, 102.0, 106.0, 116.0],
        "Low": [98.0, 98.0, 97.0, 99.0],
        "Close": [100.0, 100.0, 100.0, 115.0]
    }, index=dates, dtype=float)

    # Index 2: Down candle (Open 105, Close 100, Low 97, High 106)
    # Index 3 (final row): Displacement up (Close 115 > High 106 * 1.01)
    obs = SMCAnalysis.detect_order_blocks(df)
    assert len(obs) == 1
    assert obs[0]["confirmation_index"] == 3
    assert obs[0]["confirmation_timestamp"] == dates[3]

def test_smc_complete_series_future_mutation_invariance():
    dates = pd.date_range("2026-01-01", periods=20)
    df = pd.DataFrame({
        "Open": [100.0]*20,
        "High": [102.0]*20,
        "Low": [98.0]*20,
        "Close": [100.0]*20
    }, index=dates, dtype=float)

    # Valid Bullish FVG confirmed at index 2
    df.iloc[0, df.columns.get_loc("High")] = 100.0
    df.iloc[2, df.columns.get_loc("Open")] = 106.0
    df.iloc[2, df.columns.get_loc("Close")] = 108.0
    df.iloc[2, df.columns.get_loc("High")] = 110.0
    df.iloc[2, df.columns.get_loc("Low")] = 105.0

    # 1. Run detection on complete original series
    fvgs_original = SMCAnalysis.detect_fvg(df)
    obs_original = SMCAnalysis.detect_order_blocks(df)

    # 2. Record all events confirmed at or before cutoff index 5
    cutoff_idx = 5
    pre_cutoff_fvgs = [f for f in fvgs_original if f["confirmation_index"] <= cutoff_idx]
    pre_cutoff_obs = [o for o in obs_original if o["confirmation_index"] <= cutoff_idx]

    # 3. Mutate only candles strictly after cutoff (index 6 onward)
    df_mutated = df.copy()
    df_mutated.iloc[6:, df_mutated.columns.get_loc("Close")] += 50.0
    df_mutated.iloc[6:, df_mutated.columns.get_loc("Open")] += 50.0
    df_mutated.iloc[6:, df_mutated.columns.get_loc("High")] += 52.0
    df_mutated.iloc[6:, df_mutated.columns.get_loc("Low")] += 48.0

    # 4. Run detection on complete mutated series
    fvgs_mutated_full = SMCAnalysis.detect_fvg(df_mutated)
    obs_mutated_full = SMCAnalysis.detect_order_blocks(df_mutated)

    pre_cutoff_fvgs_mutated = [f for f in fvgs_mutated_full if f["confirmation_index"] <= cutoff_idx]
    pre_cutoff_obs_mutated = [o for o in obs_mutated_full if o["confirmation_index"] <= cutoff_idx]

    # 5. Compare pre-cutoff event identities, directions, boundaries, indices, and timestamps
    assert len(pre_cutoff_fvgs) == len(pre_cutoff_fvgs_mutated)
    for orig, mut in zip(pre_cutoff_fvgs, pre_cutoff_fvgs_mutated):
        assert orig["type"] == mut["type"]
        assert orig["pattern_index"] == mut["pattern_index"]
        assert orig["confirmation_index"] == mut["confirmation_index"]
        assert orig["top"] == mut["top"]
        assert orig["bottom"] == mut["bottom"]
        assert orig["confirmation_timestamp"] == mut["confirmation_timestamp"]

    assert len(pre_cutoff_obs) == len(pre_cutoff_obs_mutated)
    for orig, mut in zip(pre_cutoff_obs, pre_cutoff_obs_mutated):
        assert orig["type"] == mut["type"]
        assert orig["zone_index"] == mut["zone_index"]
        assert orig["confirmation_index"] == mut["confirmation_index"]
        assert orig["price"] == mut["price"]
        assert orig["confirmation_timestamp"] == mut["confirmation_timestamp"]
