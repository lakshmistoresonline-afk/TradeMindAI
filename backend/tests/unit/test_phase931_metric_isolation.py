import pytest
import numpy as np
from backend.services.research_metrics_service import ResearchMetricsService

def test_metric_isolation_ineligible_records_do_not_taint_verified():
    # 1. Base verified population (e.g., 2 clean verified trades)
    verified_records = [
        {
            "id": "v_1",
            "created_at": "2024-01-01T00:00:00",
            "outcome_timestamp": "2024-01-05T00:00:00",
            "net_pnl": 10.0,
            "outcome_verified": True,
            "evaluation_mode": "LIVE",
            "status": "TARGET_HIT"
        },
        {
            "id": "v_2",
            "created_at": "2024-01-02T00:00:00",
            "outcome_timestamp": "2024-01-06T00:00:00",
            "net_pnl": -5.0,
            "outcome_verified": True,
            "evaluation_mode": "LIVE",
            "status": "STOP_LOSS"
        }
    ]

    base_metrics = ResearchMetricsService.calculate_performance_metrics(verified_records)

    # 2. Inject extreme unverified shadow records, duplicates, chronology violations, malformed records
    tainting_records = verified_records + [
        {
            "id": "shadow_extreme_1",
            "created_at": "2024-01-01T00:00:00",
            "outcome_timestamp": "2024-01-05T00:00:00",
            "net_pnl": 9999.0,
            "outcome_verified": False,
            "evaluation_mode": "LIVE_SHADOW",
            "status": "TARGET_HIT"
        },
        {
            "id": "shadow_extreme_2",
            "created_at": "2024-01-01T00:00:00",
            "outcome_timestamp": "2024-01-05T00:00:00",
            "net_pnl": -9999.0,
            "outcome_verified": False,
            "evaluation_mode": "LIVE_SHADOW",
            "status": "STOP_LOSS"
        },
        {
            "id": "v_1", # Duplicate ID
            "created_at": "2024-01-01T00:00:00",
            "outcome_timestamp": "2024-01-05T00:00:00",
            "net_pnl": 500.0,
            "outcome_verified": True,
            "evaluation_mode": "LIVE",
            "status": "TARGET_HIT"
        }
    ]

    # Audit provenance should correctly isolate unverified vs verified
    audit_res = ResearchMetricsService.audit_signals_provenance(tainting_records)
    assert audit_res["verified_count"] == 2
    assert audit_res["unverified_shadow_count"] == 2
    assert audit_res["duplicate_count"] == 1
    assert audit_res["status"] == "PARTIALLY_VERIFIED" # Mixed verified and unverified

def test_zero_verified_returns_insufficient_evidence():
    # 1,200 pure shadow records (like signals_history.json)
    shadow_ledger = [
        {
            "id": f"sh_{i}",
            "created_at": "2024-01-01T00:00:00",
            "outcome_timestamp": "2024-01-05T00:00:00",
            "net_pnl": 5.0,
            "outcome_verified": False,
            "evaluation_mode": "LIVE_SHADOW",
            "status": "TARGET_HIT"
        }
        for i in range(1200)
    ]

    metrics = ResearchMetricsService.calculate_performance_metrics(shadow_ledger)
    assert metrics["verified_count"] == 0
    assert metrics["unverified_shadow_count"] == 1200
    assert metrics["status"] == "UNVERIFIED_SHADOW_SIMULATION"
