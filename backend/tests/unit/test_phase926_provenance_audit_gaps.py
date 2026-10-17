import pytest
import datetime
from backend.services.research_metrics_service import ResearchMetricsService

def test_provenance_fail_closed_edge_cases():
    # Case 1: outcome_verified = True, but missing evaluation_mode -> must be unverified (fail closed)
    rec1 = {
        "id": "r1",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 10.0,
        "outcome_verified": True,
        # missing evaluation_mode
        "status": "TARGET_HIT"
    }
    audit1 = ResearchMetricsService.audit_signals_provenance([rec1])
    assert audit1["verified_count"] == 0
    assert audit1["unverified_shadow_count"] == 1

    # Case 2: outcome_verified = True, unknown evaluation_mode -> unverified
    rec2 = {
        "id": "r2",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 10.0,
        "outcome_verified": True,
        "evaluation_mode": "UNKNOWN_MODE",
        "status": "TARGET_HIT"
    }
    audit2 = ResearchMetricsService.audit_signals_provenance([rec2])
    assert audit2["verified_count"] == 0
    assert audit2["unverified_shadow_count"] == 1

    # Case 3: Missing/null verification flags -> unverified
    rec3 = {
        "id": "r3",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 10.0,
        "outcome_verified": None,
        "evaluation_mode": None,
        "status": "TARGET_HIT"
    }
    audit3 = ResearchMetricsService.audit_signals_provenance([rec3])
    assert audit3["verified_count"] == 0
    assert audit3["unverified_shadow_count"] == 1

    # Case 4: Mixed verified and unverified records -> PARTIALLY_VERIFIED
    rec_live = {
        "id": "r_live",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 10.0,
        "outcome_verified": True,
        "evaluation_mode": "LIVE",
        "status": "TARGET_HIT"
    }
    rec_shad = {
        "id": "r_shad",
        "created_at": "2024-01-01T00:00:00",
        "outcome_timestamp": "2024-01-05T00:00:00",
        "net_pnl": 10.0,
        "outcome_verified": False,
        "evaluation_mode": "LIVE_SHADOW",
        "status": "TARGET_HIT"
    }
    audit_mixed = ResearchMetricsService.audit_signals_provenance([rec_live, rec_shad])
    assert audit_mixed["verified_count"] == 1
    assert audit_mixed["unverified_shadow_count"] == 1
    assert audit_mixed["status"] == "PARTIALLY_VERIFIED"
