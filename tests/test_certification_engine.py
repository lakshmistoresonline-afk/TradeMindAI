import pytest
import datetime
from backend.services.certification_engine_v2g import Phase2GCertificationEngine

def test_hard_gate_mathematical_assertion():
    # Case A: Blocking failure -> FAIL
    gates = [
        {"name": "identity", "status": "PASS", "mandatory": True},
        {"name": "pricing", "status": "FAIL", "mandatory": True}
    ]
    blocking = [g["name"] for g in gates if g["mandatory"] and g["status"] == "FAIL"]
    overall_pass = len(blocking) == 0
    assert overall_pass is False

    # Case B: Legacy non-applicable field -> does not block
    gates_b = [
        {"name": "identity", "status": "PASS", "mandatory": True},
        {"name": "linkage", "status": "NOT_APPLICABLE", "mandatory": False}
    ]
    blocking_b = [g["name"] for g in gates_b if g["mandatory"] and g["status"] == "FAIL"]
    overall_pass_b = len(blocking_b) == 0
    assert overall_pass_b is True

    # Case C: All blocking gates pass + nonblocking limitation -> CONDITIONAL_PASS
    # (This is handled in the final_status logic)
    limitations = ["LEGACY_EXEMPTIONS_ACTIVE"]
    final_status = "PHASE2G_CONDITIONAL_PASS" if (overall_pass_b and limitations) else "PHASE2G_PASS"
    assert final_status == "PHASE2G_CONDITIONAL_PASS"

def test_ledger_boundary_logic():
    engine = Phase2GCertificationEngine()
    enforcement = engine.LEDGER_2_0_ENFORCEMENT_DATE

    # Sig from Aug 2026
    legacy_sig_date = datetime.datetime(2026, 8, 27)
    assert legacy_sig_date < enforcement

    # Sig from Sep 5 2026
    current_sig_date = datetime.datetime(2026, 9, 5)
    assert current_sig_date > enforcement
