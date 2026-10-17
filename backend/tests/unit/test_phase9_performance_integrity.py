import pytest
import pandas as pd
from backend.services.research_metrics_service import ResearchMetricsService

def test_research_metrics_win_rate_and_expired_exclusion():
    # EXPIRED outcomes must be excluded from win rate denominator and directional financial aggregates
    signals = [
        {"symbol": "TCS", "status": "TARGET_HIT", "net_pnl": 5.0, "signal_type": "SWING"},
        {"symbol": "SBIN", "status": "STOP_LOSS", "net_pnl": -2.0, "signal_type": "SWING"},
        {"symbol": "INFY", "status": "EXPIRED", "net_pnl": 0.0, "signal_type": "SWING"}, # Expired should be excluded from trade count
    ]

    metrics = ResearchMetricsService.calculate_performance_metrics(signals)
    assert metrics["sample_size"] == 3
    assert metrics["eligible_directional_outcomes"] == 2
    assert metrics["wins"] == 1
    assert metrics["losses"] == 1
    assert metrics["win_rate"] == 50.0

def test_research_metrics_profit_factor_calculation():
    signals = [
        {"symbol": "A", "status": "TARGET_HIT", "net_pnl": 10.0},
        {"symbol": "B", "status": "TARGET_HIT", "net_pnl": 20.0},
        {"symbol": "C", "status": "STOP_LOSS", "net_pnl": -5.0},
        {"symbol": "D", "status": "STOP_LOSS", "net_pnl": -5.0},
    ]
    # Gross profit = 30.0, Gross loss = 10.0 -> Profit factor = 30 / 10 = 3.0
    metrics = ResearchMetricsService.calculate_performance_metrics(signals)
    assert metrics["profit_factor"] == 3.0
    assert metrics["net_pnl"] == 20.0

def test_research_metrics_zero_gross_loss_profit_factor():
    signals = [
        {"symbol": "A", "status": "TARGET_HIT", "net_pnl": 10.0},
        {"symbol": "B", "status": "TARGET_HIT", "net_pnl": 15.0},
    ]
    # Zero gross loss yields profit_factor None
    metrics = ResearchMetricsService.calculate_performance_metrics(signals)
    assert metrics["profit_factor"] is None
    assert metrics["net_pnl"] == 25.0

def test_research_metrics_incomplete_data_handling():
    signals = [
        {"symbol": "A", "status": "TARGET_HIT", "net_pnl": None},
    ]
    metrics = ResearchMetricsService.calculate_performance_metrics(signals)
    assert metrics["financial_status"] == "INCOMPLETE_DATA"
    assert metrics["net_pnl"] is None
    assert metrics["profit_factor"] is None
