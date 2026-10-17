import pytest
import datetime
from backend.services.research_metrics_service import ResearchMetricsService

def test_zero_verified_records_never_yields_verified_claim_regression():
    # 1. Records with outcome_verified = False or missing outcome_verified
    records = [
        {
            "id": "reg_1",
            "created_at": "2024-01-01T00:00:00",
            "outcome_timestamp": "2024-01-05T00:00:00",
            "net_pnl": 10.0,
            "outcome_verified": False,
            "evaluation_mode": "LIVE_SHADOW",
            "status": "TARGET_HIT"
        },
        {
            "id": "reg_2",
            "created_at": "2024-01-02T00:00:00",
            "outcome_timestamp": "2024-01-06T00:00:00",
            "net_pnl": -5.0,
            # missing outcome_verified -> defaults to unverified / fail-closed
            "evaluation_mode": "LIVE",
            "status": "STOP_LOSS"
        }
    ]

    audit = ResearchMetricsService.audit_signals_provenance(records)
    assert audit["verified_count"] == 0
    assert audit["status"] != "VERIFIED"

    metrics = ResearchMetricsService.calculate_performance_metrics(records)
    assert metrics["status"] != "VERIFIED"
    assert metrics["status"] == "UNVERIFIED_SHADOW_SIMULATION"
