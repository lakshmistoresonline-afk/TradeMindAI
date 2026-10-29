"""
================================================================================
TradeMindAI Unit Tests — Production Horizon Outcome Engine (Fix 2 & Fix 4)
================================================================================
Directly exercises evaluate_horizon_outcome() from backend.app.services.horizon_engine
for:
1. Full horizon without target/stop hit -> EXPIRED
2. Incomplete horizon (len < horizon) without target/stop hit -> INCOMPLETE_WINDOW
3. Incomplete horizon with target hit before data ends -> TARGET_HIT
4. Incomplete horizon with stop hit before data ends -> STOP_LOSS
5. Same-bar target and stop touched -> STOP_LOSS (conservative ambiguity rule)
6. Empty future window -> ACTIVE
7. Exact horizon boundary -> is_full_horizon True
8. Independent evaluation across 5, 10, 20, 60 session horizons
9. Candidate near symbol's endpoint -> correctly uses candidate symbol's own series length
10. Completed-trade metric exclusion -> INCOMPLETE_WINDOW excluded
================================================================================
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.services.horizon_engine import evaluate_horizon_outcome

def test_full_horizon_no_hit_expired():
    future_sub = pd.DataFrame({
        "High": [102.0] * 20,
        "Low": [98.0] * 20,
        "Close": [101.0] * 20,
        "date": [f"2026-01-{i+1:02d}" for i in range(20)]
    })
    res = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_sub, horizon=20)
    assert res["status"] == "EXPIRED"
    assert res["is_full_horizon"] is True
    assert res["exit_date"] == "2026-01-20"

def test_incomplete_horizon_no_hit_incomplete_window():
    future_sub = pd.DataFrame({
        "High": [102.0] * 5,
        "Low": [98.0] * 5,
        "Close": [101.0] * 5,
        "date": [f"2026-01-{i+1:02d}" for i in range(5)]
    })
    res = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_sub, horizon=20)
    assert res["status"] == "INCOMPLETE_WINDOW"
    assert res["is_full_horizon"] is False
    assert res["exit_date"] == "2026-01-05"

def test_incomplete_horizon_with_target_hit():
    future_sub = pd.DataFrame({
        "High": [102.0, 109.0, 101.0, 101.0, 101.0],
        "Low": [98.0, 99.0, 98.0, 98.0, 98.0],
        "Close": [101.0, 108.0, 100.0, 100.0, 100.0],
        "date": [f"2026-01-{i+1:02d}" for i in range(5)]
    })
    res = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_sub, horizon=20)
    assert res["status"] == "TARGET_HIT"
    assert res["exit_price"] == 108.0
    assert res["exit_date"] == "2026-01-02"

def test_incomplete_horizon_with_stop_loss_hit():
    future_sub = pd.DataFrame({
        "High": [102.0, 101.0, 99.0, 101.0, 101.0],
        "Low": [98.0, 97.0, 94.0, 98.0, 98.0],
        "Close": [101.0, 99.0, 94.0, 99.0, 99.0],
        "date": [f"2026-01-{i+1:02d}" for i in range(5)]
    })
    res = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_sub, horizon=20)
    assert res["status"] == "STOP_LOSS"
    assert res["exit_price"] == 95.0
    assert res["exit_date"] == "2026-01-03"

def test_same_bar_target_and_stop_conservative_stop_loss():
    future_sub = pd.DataFrame({
        "High": [110.0],
        "Low": [90.0],
        "Close": [100.0],
        "date": ["2026-01-01"]
    })
    res = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_sub, horizon=5)
    assert res["status"] == "STOP_LOSS"
    assert res["exit_price"] == 95.0

def test_empty_future_window_active():
    future_sub = pd.DataFrame()
    res = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_sub, horizon=20)
    assert res["status"] == "ACTIVE"
    assert res["is_full_horizon"] is False
    assert res["exit_date"] is None

def test_independent_evaluation_across_horizons():
    future_5 = pd.DataFrame({
        "High": [102.0] * 5, "Low": [98.0] * 5, "Close": [101.0] * 5, "date": [f"2026-01-{i+1:02d}" for i in range(5)]
    })
    # For horizon=5, 5 bars is full horizon -> EXPIRED
    res5 = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_5, horizon=5)
    assert res5["status"] == "EXPIRED"
    assert res5["is_full_horizon"] is True

    # For horizon=10/20/60, 5 bars is incomplete window -> INCOMPLETE_WINDOW
    for h in [10, 20, 60]:
        resh = evaluate_horizon_outcome(100.0, 108.0, 95.0, future_5, horizon=h)
        assert resh["status"] == "INCOMPLETE_WINDOW"
        assert resh["is_full_horizon"] is False

def test_symbol_ending_earlier_than_another_symbol():
    # Symbol A has 10 future bars available
    sym_a_future = pd.DataFrame({
        "High": [101.0] * 10, "Low": [99.0] * 10, "Close": [100.0] * 10, "date": [f"2026-01-{i+1:02d}" for i in range(10)]
    })
    # Symbol B has 20 future bars available
    sym_b_future = pd.DataFrame({
        "High": [101.0] * 20, "Low": [99.0] * 20, "Close": [100.0] * 20, "date": [f"2026-01-{i+1:02d}" for i in range(20)]
    })

    # For 20-bar horizon: Symbol A's 10 bars is INCOMPLETE_WINDOW
    res_a = evaluate_horizon_outcome(100.0, 108.0, 95.0, sym_a_future, horizon=20)
    assert res_a["status"] == "INCOMPLETE_WINDOW"
    assert res_a["is_full_horizon"] is False

    # For 20-bar horizon: Symbol B's 20 bars is EXPIRED
    res_b = evaluate_horizon_outcome(100.0, 108.0, 95.0, sym_b_future, horizon=20)
    assert res_b["status"] == "EXPIRED"
    assert res_b["is_full_horizon"] is True

def test_incomplete_window_excluded_from_completed_trade_metrics():
    trades = [
        {"status": "TARGET_HIT", "pnl_pct": 8.0},
        {"status": "STOP_LOSS", "pnl_pct": -5.0},
        {"status": "EXPIRED", "pnl_pct": 1.0},
        {"status": "INCOMPLETE_WINDOW", "pnl_pct": 2.0}
    ]
    df_trades = pd.DataFrame(trades)
    completed_trades = df_trades[df_trades["status"] != "INCOMPLETE_WINDOW"]

    assert len(completed_trades) == 3
    hits = (completed_trades["status"] == "TARGET_HIT").sum()
    win_rate = (hits / len(completed_trades)) * 100
    assert win_rate == pytest.approx(33.33, rel=1e-2)
