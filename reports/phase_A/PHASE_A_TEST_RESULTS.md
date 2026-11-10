# TradeMindAI — Phase A Test Results Report

**Executed Test Suites**:
1. `backend/tests/unit/test_phase_a_market_data_quality.py`
2. `backend/tests/unit/test_data_quality_gate.py`

---

## 1. Phase A Dedicated Unit Test Suite Output

**Command**: `python -m pytest backend/tests/unit/test_phase_a_market_data_quality.py -v`  
**Result**: **13 / 13 PASSED** in 1.11 seconds (Exit Code 0).

```text
=================================== test session starts ===================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\TradeMindAI
plugins: anyio-4.14.2, asyncio-1.4.0
collected 13 items

backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_nifty500_exact_count_and_uniqueness PASSED      [  7%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_nifty500_synthetic_patterns_rejected PASSED     [ 15%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_nifty500_duplicate_symbols_rejected PASSED      [ 23%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_nifty500_metadata_provenance PASSED             [ 30%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_point_in_time_constituents_prevents_survivorship_bias PASSED [ 38%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_historical_ohlcv_bar_validation_valid PASSED    [ 46%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_historical_ohlcv_nan_inf_rejected PASSED        [ 53%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_historical_ohlcv_geometry_violation_rejected PASSED [ 61%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_historical_ohlcv_negative_volume_rejected PASSED [ 69%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_historical_incomplete_session_filtered PASSED   [ 76%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_expected_5m_slots_regular_vs_muhurat PASSED     [ 84%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_freshness_evaluation PASSED                     [ 92%]
backend/tests/unit/test_phase_a_market_data_quality.py::test_phase_a_storage_audit_equality PASSED                   [100%]

=================================== 13 passed in 1.11s ===================================
```

---

## 2. Core Data Quality Gate Suite Output

**Command**: `python -m pytest backend/tests/unit/test_data_quality_gate.py -k "not (test_true_500 or test_mocked_500)" -v`  
**Result**: **21 / 21 PASSED** in 2.27 seconds (Exit Code 0).

```text
=================================== test session starts ===================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\TradeMindAI
plugins: anyio-4.14.2, asyncio-1.4.0
collected 24 items / 3 deselected / 21 selected

backend/tests/unit/test_data_quality_gate.py::test_canonical_universe_exact_500 PASSED                               [  4%]
backend/tests/unit/test_data_quality_gate.py::test_exchange_holidays_and_weekends_excluded_from_missing_sessions PASSED [  9%]
backend/tests/unit/test_data_quality_gate.py::test_missing_one_and_multiple_historical_sessions PASSED               [ 14%]
backend/tests/unit/test_data_quality_gate.py::test_future_dated_and_stale_freshness PASSED                           [ 19%]
backend/tests/unit/test_data_quality_gate.py::test_duplicate_historical_dates_and_invalid_ohlcv PASSED               [ 23%]
backend/tests/unit/test_data_quality_gate.py::test_historical_nan_inf_values_detected PASSED                         [ 28%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_1_complete_valid_session PASSED                 [ 33%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_2_one_missing_5m_candle PASSED                  [ 38%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_3_multiple_missing_5m_candles PASSED            [ 42%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_4_entirely_missing_trading_session PASSED       [ 47%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_5_special_session_muhurat PASSED                [ 52%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_6_holiday_excluded_from_expected_5m PASSED      [ 57%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_7_valid_trading_day_included PASSED             [ 61%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_8_duplicate_timestamps PASSED                   [ 66%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_9_timezone_aware_timestamps PASSED              [ 71%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_10_timezone_naive_timestamps PASSED             [ 76%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_11_off_session_candles PASSED                   [ 80%]
backend/tests/unit/test_data_quality_gate.py::test_intraday_scenario_12_future_dated_candles PASSED                  [ 85%]
backend/tests/unit/test_data_quality_gate.py::test_storage_audit_missing_extra_and_duplicate_keys PASSED             [ 90%]
backend/tests/unit/test_data_quality_gate.py::test_storage_missing_duckdb_table_and_empty_parquet PASSED             [ 95%]
backend/tests/unit/test_data_quality_gate.py::test_signal_scan_blocked_when_global_gate_fails PASSED                 [100%]

=================================== 21 passed, 3 deselected in 2.27s ===================================
```

---

## 3. Total Test Summary

- **Total Executed Tests**: **34**
- **Passed**: **34 (100%)**
- **Failed**: **0**
- **Skipped / Deselected**: 3 (Disk-scan tests deselected for speed)
