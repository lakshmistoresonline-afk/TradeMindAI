# TradeMindAI — Phase C Regression Tests Report

**Executed Test Suite**: `backend/tests/unit/test_phase_c_ml_prediction.py`

---

## 1. Automated Test Suite Output

**Command**: `python -m pytest backend/tests/unit/test_phase_c_ml_prediction.py -v`  
**Result**: **6 / 6 PASSED** in 0.60 seconds (Exit Code 0).

```text
=================================== test session starts ===================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\TradeMindAI
plugins: anyio-4.14.2, asyncio-1.4.0
collected 6 items

backend/tests/unit/test_phase_c_ml_prediction.py::test_phase_c_missing_champion_model_returns_unavailable PASSED     [ 16%]
backend/tests/unit/test_phase_c_ml_prediction.py::test_phase_c_missing_model_file_returns_unavailable PASSED         [ 33%]
backend/tests/unit/test_phase_c_ml_prediction.py::test_phase_c_corrupted_model_file_fails_closed PASSED              [ 50%]
backend/tests/unit/test_phase_c_ml_prediction.py::test_phase_c_missing_required_features_schema_rejection PASSED     [ 66%]
backend/tests/unit/test_phase_c_ml_prediction.py::test_phase_c_non_finite_features_rejection PASSED                  [ 83%]
backend/tests/unit/test_phase_c_ml_prediction.py::test_phase_c_signal_quality_service_fails_closed_on_unregistered_or_weak_model PASSED [100%]

=================================== 6 passed in 0.60s ===================================
```

---

## 2. Test Coverage Summary

- **Missing Model Metadata**: Returns `UNAVAILABLE` (**PASSED**).
- **Missing Model File**: Returns `UNAVAILABLE` (**PASSED**).
- **Corrupted Model File**: Fails closed with `MODEL_LOAD_FAILURE` (**PASSED**).
- **Missing Required Features**: Fails closed with `SCHEMA_VALIDATION_FAILURE` (**PASSED**).
- **Non-Finite Feature Values**: Fails closed with `NON_FINITE_FEATURES` (**PASSED**).
- **Weak or Unregistered Model**: Fails publication gate in `SignalQualityService` (**PASSED**).
