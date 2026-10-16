import pytest
import math
import numpy as np
from backend.api.v1.endpoints.equity import calculate_auc_with_ties, is_eligible_buy
from backend.services.research_metrics_service import ResearchMetricsService

# --- AUC TESTS ---
def test_auc_perfect_ranking():
    y_true = [0.0, 0.0, 1.0, 1.0]
    y_prob = [0.1, 0.2, 0.8, 0.9]
    assert calculate_auc_with_ties(y_true, y_prob) == 1.0

def test_auc_reversed_ranking():
    y_true = [0.0, 0.0, 1.0, 1.0]
    y_prob = [0.9, 0.8, 0.2, 0.1]
    assert calculate_auc_with_ties(y_true, y_prob) == 0.0

def test_auc_all_tied_with_both_classes():
    y_true = [0.0, 0.0, 1.0, 1.0]
    y_prob = [0.5, 0.5, 0.5, 0.5]
    assert calculate_auc_with_ties(y_true, y_prob) == 0.5

def test_auc_partial_tie_exact():
    y_true = [0.0, 1.0, 0.0, 1.0]
    y_prob = [0.3, 0.3, 0.3, 0.7]
    assert calculate_auc_with_ties(y_true, y_prob) == 0.75

def test_auc_single_class():
    y_true = [1.0, 1.0, 1.0]
    y_prob = [0.6, 0.7, 0.8]
    assert calculate_auc_with_ties(y_true, y_prob) is None

def test_auc_invalid_inputs():
    assert calculate_auc_with_ties([1.0], [0.5]) is None
    assert calculate_auc_with_ties([0.0, 1.0], [0.5, float('nan')]) is None
    assert calculate_auc_with_ties([0.0, 1.0], [0.5, float('inf')]) is None
    assert calculate_auc_with_ties([0.0, 1.0], [0.5, 1.2]) is None


# --- BUY ELIGIBILITY TESTS ---
def test_buy_eligibility_orm_and_dicts():
    class MockORM:
        def __init__(self, direction, rating, signal_rating=None):
            self.direction = direction
            self.rating = rating
            self.signal_rating = signal_rating

    assert is_eligible_buy(MockORM("LONG", "BUY")) is True
    assert is_eligible_buy(MockORM("LONG", "STRONG_BUY")) is True
    assert is_eligible_buy({"direction": "LONG", "rating": "BUY"}) is True
    assert is_eligible_buy(MockORM("SHORT", "BUY")) is False
    assert is_eligible_buy(MockORM("LONG", "SELL")) is False
    assert is_eligible_buy(MockORM("LONG", "BUY", signal_rating="SELL")) is False
    assert is_eligible_buy(MockORM("LONG", "SELL", signal_rating="BUY")) is False
    assert is_eligible_buy(MockORM(None, "BUY")) is False
    assert is_eligible_buy(MockORM("LONG", None)) is False
    assert is_eligible_buy(None) is False


# --- RESEARCH METRICS SERVICE TESTS ---
def test_research_metrics_empty_ledger():
    res = ResearchMetricsService.calculate_performance_metrics([])
    assert res["sample_size"] == 0
    assert res["status"] == "INSUFFICIENT_EVIDENCE"
    assert res["win_rate"] is None
    assert res["net_pnl"] is None

def test_research_metrics_only_expired():
    signals = [
        {"status": "EXPIRED", "net_pnl": 0.0, "calibrated_probability": 0.5, "outcome_binary": 0},
        {"status": "EXPIRED", "net_pnl": 0.1, "calibrated_probability": 0.4, "outcome_binary": 0}
    ]
    res = ResearchMetricsService.calculate_performance_metrics(signals)
    assert res["sample_size"] == 2
    assert res["eligible_directional_outcomes"] == 0
    assert res["status"] == "INSUFFICIENT_EVIDENCE"
    assert res["win_rate"] is None
    assert res["net_pnl"] is None

def test_research_metrics_mixture_with_expired():
    signals = [
        {"status": "TARGET_HIT", "net_pnl": 5.0, "calibrated_probability": 0.8, "outcome_binary": 1},
        {"status": "STOP_LOSS", "net_pnl": -3.0, "calibrated_probability": 0.6, "outcome_binary": 0},
        {"status": "EXPIRED", "net_pnl": 100.0, "calibrated_probability": 0.5, "outcome_binary": 0}
    ]
    res = ResearchMetricsService.calculate_performance_metrics(signals)
    assert res["sample_size"] == 3
    assert res["eligible_directional_outcomes"] == 2
    assert res["wins"] == 1
    assert res["losses"] == 1
    assert res["win_rate"] == 50.0
    # Expired net_pnl is excluded from directional realized net_pnl sum
    assert res["net_pnl"] == 2.0

def test_research_metrics_partial_pnl_completeness():
    signals = [
        {"status": "TARGET_HIT", "net_pnl": 5.0, "calibrated_probability": 0.8, "outcome_binary": 1},
        {"status": "STOP_LOSS", "net_pnl": float('nan'), "calibrated_probability": 0.6, "outcome_binary": 0}
    ]
    res = ResearchMetricsService.calculate_performance_metrics(signals)
    assert res["sample_size"] == 2
    assert res["wins"] == 1
    assert res["losses"] == 1
    assert res["win_rate"] == 50.0
    # Financial metrics return None when directional P&L data is incomplete
    assert res["net_pnl"] is None
    assert res["expectancy"] is None
    assert res["profit_factor"] is None

def test_research_metrics_zero_gross_loss_profit_factor():
    signals = [
        {"status": "TARGET_HIT", "net_pnl": 5.0, "calibrated_probability": 0.8, "outcome_binary": 1},
        {"status": "TARGET_HIT", "net_pnl": 10.0, "calibrated_probability": 0.9, "outcome_binary": 1}
    ]
    res = ResearchMetricsService.calculate_performance_metrics(signals)
    assert res["wins"] == 2
    assert res["losses"] == 0
    assert res["win_rate"] == 100.0
    assert res["net_pnl"] == 15.0
    # Gross loss == 0 yields profit_factor None (not infinity)
    assert res["profit_factor"] is None

def test_brier_score_validation_edge_cases():
    # Out-of-bounds probability (> 1.0)
    signals_bad_prob = [
        {"status": "TARGET_HIT", "net_pnl": 5.0, "calibrated_probability": 1.5, "outcome_binary": 1}
    ]
    res1 = ResearchMetricsService.calculate_performance_metrics(signals_bad_prob)
    assert res1["brier_score"] is None

    # Non-binary outcome (2)
    signals_bad_outcome = [
        {"status": "TARGET_HIT", "net_pnl": 5.0, "calibrated_probability": 0.8, "outcome_binary": 2}
    ]
    res2 = ResearchMetricsService.calculate_performance_metrics(signals_bad_outcome)
    assert res2["brier_score"] is None

    # Inf and NaN probability
    signals_nan_inf = [
        {"status": "TARGET_HIT", "net_pnl": 5.0, "calibrated_probability": float('inf'), "outcome_binary": 1},
        {"status": "STOP_LOSS", "net_pnl": -2.0, "calibrated_probability": float('nan'), "outcome_binary": 0}
    ]
    res3 = ResearchMetricsService.calculate_performance_metrics(signals_nan_inf)
    assert res3["brier_score"] is None

    # Valid probability and binary outcome
    signals_valid = [
        {"status": "TARGET_HIT", "net_pnl": 5.0, "calibrated_probability": 0.8, "outcome_binary": 1},
        {"status": "STOP_LOSS", "net_pnl": -2.0, "calibrated_probability": 0.2, "outcome_binary": 0}
    ]
    res4 = ResearchMetricsService.calculate_performance_metrics(signals_valid)
    assert res4["brier_score"] == 0.04
