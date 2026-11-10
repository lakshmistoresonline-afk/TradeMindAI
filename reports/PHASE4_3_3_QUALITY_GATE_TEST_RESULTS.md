# Phase 4.3.3 Quality Gate Test Results Report

**Date**: 2026-11-03  
**Test Suite**: `backend/tests/unit/test_phase4_3_3_quality_and_pipeline.py`  
**Status**: **7/7 PASSED (100%)**

| Test Case Name | Input Conditions | Expected | Actual |
| :--- | :--- | :---: | :---: |
| `test_effective_signals_only_safety_invariant` | `REAL_TRADING=False`, `QUARANTINE_ACTIVE=True` | `True` | **PASSED** |
| `test_trading_safety_prohibits_order_execution` | `execute_order()` called | `TradingSafetyViolation` | **PASSED** |
| `test_quality_gate_strict_fail_closed_unregistered_model` | `model = None`, `calibrated_prob = 0.82` | `False` | **PASSED** |
| `test_quality_gate_registered_model_success` | Valid `ModelMetadata`, `test_size=50`, `roc_auc=0.65` | `True` | **PASSED** |
| `test_quality_gate_insufficient_sample_size_rejected` | Valid `ModelMetadata`, `test_size=10 < 20` | `False` | **PASSED** |
| `test_end_to_end_controlled_signal_persistence_and_readback` | Valid `LiveSignal` + `SessionLocal` write | `PERSISTED` + Readback | **PASSED** |
| `test_frozen_v22_files_byte_integrity` | 5 frozen V2.2 SHA-256 hashes | Match | **PASSED** |
