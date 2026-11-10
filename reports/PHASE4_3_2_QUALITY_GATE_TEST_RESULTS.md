# Phase 4.3.2 Quality Gate Test Results Report

**Date**: 2026-11-03  
**Test Suite**: `backend/tests/unit/test_phase4_3_2_quality_and_pipeline.py`  
**Status**: **6/6 PASSED (100%)**

| Test Case Name | Input Conditions | Expected Outcome | Actual Result |
| :--- | :--- | :---: | :---: |
| `test_quality_gate_strict_fail_closed_unregistered_model` | `model = None`, `calibrated_prob = 0.82` | `False` | **PASSED** |
| `test_quality_gate_registered_model_success` | `model` valid, `test_size=50`, `roc_auc=0.65` | `True` | **PASSED** |
| `test_quality_gate_insufficient_sample_size_rejected` | `model` valid, `test_size=10 < 20` | `False` | **PASSED** |
| `test_quality_gate_low_probability_rejected` | `model` valid, `calibrated_prob=0.45 < 0.52` | `False` | **PASSED** |
| `test_security_master_bagmane_audit` | Symbol `BAGMANE` security master lookup | Mapped | **PASSED** |
| `test_safety_invariants_strictly_enforced` | `REAL_TRADING=False`, `QUARANTINE_ACTIVE=True` | Enforced | **PASSED** |
