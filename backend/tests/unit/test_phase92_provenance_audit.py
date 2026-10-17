import pytest
import datetime
from backend.services.research_metrics_service import ResearchMetricsService

def test_audit_signals_provenance_comprehensive():
    # 1. Valid verified record
    rec_valid = {
        "id": "rec_1",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 10.0,
        "outcome_verified": True,
        "evaluation_mode": "LIVE",
        "status": "TARGET_HIT"
    }

    # 2. Unverified shadow record
    rec_shadow = {
        "id": "rec_2",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 15.0,
        "outcome_verified": False,
        "evaluation_mode": "LIVE_SHADOW",
        "status": "TARGET_HIT"
    }

    # 3. Chronology invalid record (signal time > outcome time)
    rec_chrono = {
        "id": "rec_3",
        "created_at": "2024-01-10T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 5.0,
        "outcome_verified": True,
        "evaluation_mode": "LIVE",
        "status": "TARGET_HIT"
    }

    # 4. Duplicate record ID
    rec_dup = {
        "id": "rec_1",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 10.0,
        "outcome_verified": True,
        "evaluation_mode": "LIVE",
        "status": "TARGET_HIT"
    }

    # 5. Incomplete financial record (missing net_pnl)
    rec_incomplete = {
        "id": "rec_5",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": None,
        "outcome_verified": True,
        "evaluation_mode": "LIVE",
        "status": "TARGET_HIT"
    }

    audit_res = ResearchMetricsService.audit_signals_provenance([rec_valid, rec_shadow, rec_chrono, rec_dup, rec_incomplete])

    assert audit_res["total_audited"] == 5
    assert audit_res["duplicate_count"] == 1
    assert audit_res["chronology_anomaly_count"] == 1
    assert audit_res["incomplete_data_count"] == 1
    assert audit_res["unverified_shadow_count"] == 1
    assert audit_res["verified_count"] == 1
    assert audit_res["status"] == "PARTIALLY_VERIFIED"

    # Test calculate_performance_metrics honoring unverified shadow status when status is present
    perf_metrics = ResearchMetricsService.calculate_performance_metrics([rec_shadow])
    assert perf_metrics["status"] == "UNVERIFIED_SHADOW_SIMULATION"

def test_zero_verified_records_never_yields_verified_claim():
    shadow_records = [
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
    metrics = ResearchMetricsService.calculate_performance_metrics(shadow_records)
    assert metrics["status"] != "VERIFIED"
    assert metrics["status"] == "UNVERIFIED_SHADOW_SIMULATION"
