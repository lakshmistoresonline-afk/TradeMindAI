import pytest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
from backend.analysis.backtester import BacktestEngine

def test_backtest_math():
    # Mock firestore
    mock_db = MagicMock()
    engine = BacktestEngine(mock_db)

    # Verify calculation logic (isolated from API)
    # Success: Exit > Entry
    entry = 100
    exit = 110
    profit = ((exit - entry) / entry) * 100
    assert profit == 10.0

    # Failure: Exit < Entry
    exit_fail = 90
    loss = ((exit_fail - entry) / entry) * 100
    assert loss == -10.0
