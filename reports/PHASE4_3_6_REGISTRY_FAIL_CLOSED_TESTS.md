# Phase 4.3.6 Registry Fail-Closed Tests Report

**Date**: 2026-11-03  
**Classification**: **VERIFIED (6/6 PASSED)**

| Test Case Name | Input Conditions | Expected | Actual |
| :--- | :--- | :---: | :---: |
| `test_isolated_test_database_guard` | `sqlite:///:memory:` check | Isolated | **PASSED** |
| `test_signals_only_runtime_safety_invariants` | `REAL_TRADING=False`, `QUARANTINE_ACTIVE=True` | `True` | **PASSED** |
| `test_symbol_identity_exact_match_enforced` | `get_champion_model("INFY")` when only `TCS` exists | `None` | **PASSED** |
| `test_missing_symbol_or_horizon_fails_closed` | Missing symbol model lookup | `None` + `False` | **PASSED** |
| `test_model_registry_json_serialization_round_trip` | Save & retrieve `ModelMetadata` with JSON dicts | Preserved | **PASSED** |
| `test_frozen_v22_files_byte_integrity_normalized` | 5 frozen V2.2 SHA-256 hashes against Git HEAD | Match | **PASSED** |
