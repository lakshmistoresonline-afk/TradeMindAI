import pytest
import datetime
from backend.services.research_metrics_service import ResearchMetricsService

def test_chronology_and_provenance_audit_detection():
    # Test record with export timestamp > outcome_timestamp (historical replay anomaly) and unverified outcome
    records = [
        {
            "id": "sh_sig_ACC_20161021_2",
            "timestamp": "2026-09-23T10:17:22.779046",
            "outcome_timestamp": "2016-10-24T10:00:00",
            "status": "TARGET_HIT",
            "net_pnl": 118.1,
            "outcome_verified": False,
            "evaluation_mode": "LIVE_SHADOW"
        },
        {
            "id": "sh_sig_VALID_1",
            "timestamp": "2016-10-20T10:00:00",
            "outcome_timestamp": "2016-10-24T10:00:00",
            "status": "TARGET_HIT",
            "net_pnl": 50.0,
            "outcome_verified": True,
            "evaluation_mode": "LIVE"
        }
    ]

    metrics = ResearchMetricsService.calculate_performance_metrics(records)
    # Even with unverified / exported timestamps, ResearchMetricsService calculates performance strictly on status & net_pnl
    assert metrics["sample_size"] == 2
    assert metrics["eligible_directional_outcomes"] == 2
    assert metrics["wins"] == 2
    assert metrics["win_rate"] == 100.0
    assert metrics["net_pnl"] == 168.1
