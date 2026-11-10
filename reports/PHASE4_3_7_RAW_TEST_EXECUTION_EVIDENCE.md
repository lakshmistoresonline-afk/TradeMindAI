# Phase 4.3.7 Raw Test Execution Evidence Report

**Date**: 2026-11-03  
**Classification**: **100% PASSED (50/50 PASSED)**

## Automated Test Suite Execution Summary

```text
=================================================== test session starts ===================================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
collected 50 items

backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py::test_isolated_test_database_guard PASSED                 [  2%]
backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py::test_signals_only_runtime_safety_invariants PASSED       [  4%]
backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py::test_symbol_identity_exact_match_enforced PASSED         [  6%]
backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py::test_missing_symbol_or_horizon_fails_closed PASSED       [  8%]
backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py::test_model_registry_json_serialization_round_trip PASSED [ 10%]
backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py::test_frozen_v22_files_byte_integrity_normalized PASSED   [ 12%]
backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py::test_effective_signals_only_safety_invariant PASSED      [ 14%]
backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py::test_trading_safety_prohibits_order_execution PASSED     [ 16%]
backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py::test_quality_gate_strict_fail_closed_unregistered_model PASSED [ 18%]
backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py::test_quality_gate_registered_model_success PASSED        [ 20%]
backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py::test_quality_gate_insufficient_sample_size_rejected PASSED [ 22%]
backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py::test_end_to_end_controlled_signal_persistence_and_readback PASSED [ 24%]
backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py::test_frozen_v22_files_byte_integrity_baseline_head PASSED [ 26%]
backend/tests/unit/test_quarantine_enforcement.py::test_quarantine_setting_defaults_to_true PASSED                   [ 28%]
...
backend/tests/unit/test_postgres_migration_cli.py::test_mock_postgres_explicit_migration_creates_index PASSED        [100%]

============================================== 50 passed, 3 warnings in 12.61s ==============================================
```
