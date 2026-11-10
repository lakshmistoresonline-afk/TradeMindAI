# TradeMindAI — Phase D Test Results Report

**Executed Test Suites**:
1. `backend/tests/unit/test_phase_d_signal_validation.py`
2. `backend/tests/unit/test_quarantine_enforcement.py`
3. `backend/tests/unit/test_signal_ledger_transaction_ownership.py`

---

## 1. Phase D Signal Validation Unit Test Suite Output

**Command**: `python -m pytest backend/tests/unit/test_phase_d_signal_validation.py -v`  
**Result**: **11 / 11 PASSED** in 0.49 seconds (Exit Code 0).

```text
=================================== test session starts ===================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\TradeMindAI
plugins: anyio-4.14.2, asyncio-1.4.0
collected 11 items

backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_valid_long_signal_passes_validation PASSED        [  9%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_valid_short_signal_passes_validation PASSED       [ 18%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_neutral_or_unavailable_direction_rejected PASSED  [ 27%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_non_finite_price_rejected PASSED                  [ 36%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_non_positive_price_rejected PASSED                [ 45%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_zero_risk_distance_rejected PASSED                [ 54%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_inverted_long_geometry_rejected PASSED            [ 63%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_inverted_short_geometry_rejected PASSED           [ 72%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_suboptimal_risk_reward_rejected PASSED            [ 81%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_weak_edge_conviction_rejected PASSED              [ 90%]
backend/tests/unit/test_phase_d_signal_validation.py::test_phase_d_missing_provenance_rejected PASSED                [100%]

=================================== 11 passed in 0.49s ===================================
```

---

## 2. Quarantine & Transaction Ownership Suite Output

**Command**: `python -m pytest backend/tests/unit/test_quarantine_enforcement.py backend/tests/unit/test_signal_ledger_transaction_ownership.py -v`  
**Result**: **45 / 45 PASSED** in 2.79 seconds (Exit Code 0).

```text
=================================== test session starts ===================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\TradeMindAI
plugins: anyio-4.14.2, asyncio-1.4.0
collected 45 items

backend/tests/unit/test_quarantine_enforcement.py::test_quarantine_setting_defaults_to_true PASSED                   [  2%]
backend/tests/unit/test_quarantine_enforcement.py::test_quarantine_cannot_be_disabled_via_override[False] PASSED       [  4%]
...
backend/tests/unit/test_signal_ledger_transaction_ownership.py::test_create_signal_internal_caller_session_flushes_only PASSED [100%]

=================================== 45 passed in 2.79s ===================================
```

---

## 3. Total Test Summary

- **Total Executed Tests**: **56**
- **Passed**: **56 (100%)**
- **Failed**: **0**
