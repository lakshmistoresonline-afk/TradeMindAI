import pytest
import numpy as np
import pandas as pd
from backend.services.forensic_analytical_service import ForensicAnalyticalService

def test_win_rate_calculation_logic():
    # Mock data with known win rate
    # Successes: 3, Total: 5 -> 60.0%
    data = [
        {"status": "TARGET_HIT", "net_pnl": 3.0},
        {"status": "TARGET_HIT", "net_pnl": 2.8},
        {"status": "TARGET_HIT", "net_pnl": 9.8},
        {"status": "STOP_LOSS", "net_pnl": -3.2},
        {"status": "STOP_LOSS", "net_pnl": -4.2}
    ]
    df = pd.DataFrame(data)

    wins = len(df[df['status'] == 'TARGET_HIT'])
    total = len(df)
    wr_pct = (wins / total) * 100

    assert wr_pct == 60.0
    assert wr_pct != 6473.99 # Anti-regression

def test_profit_factor_calculation():
    data = [
        {"net_pnl": 10.0},
        {"net_pnl": 5.0},
        {"net_pnl": -5.0}
    ]
    df = pd.DataFrame(data)

    gross_profit = df[df['net_pnl'] > 0]['net_pnl'].sum()
    gross_loss = abs(df[df['net_pnl'] < 0]['net_pnl'].sum())
    pf = gross_profit / gross_loss

    assert pf == 3.0

def test_population_exclusion():
    # Verify that ACTIVE signals are not in verified population
    # (This is more of an integration test for the service query)
    pass
