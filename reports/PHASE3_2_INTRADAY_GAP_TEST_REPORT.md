# Phase 3.2.1 Intraday Gap Test Report

**Date**: 2026-11-03  
**Executable Unit Tests**: 12/12  
**Test Suite File**: `backend/tests/unit/test_data_quality_gate.py`  
**Test Result**: **100% PASSED** (24 total data quality gate unit tests)

## 12 Executable Intraday Test Scenarios

1. `test_intraday_scenario_1_complete_valid_session`: Validates 75 expected slots (`09:15:00` to `15:25:00` IST) -> `PASS`.
2. `test_intraday_scenario_2_one_missing_5m_candle`: 74 slots provided -> `missing_intervals = 1` -> `PARTIAL`.
3. `test_intraday_scenario_3_multiple_missing_5m_candles`: 65 slots provided -> `missing_intervals = 10` -> `PARTIAL`.
4. `test_intraday_scenario_4_entirely_missing_trading_session`: 0 slots provided -> `missing_intervals = 75` -> `PARTIAL`.
5. `test_intraday_scenario_5_special_session_muhurat`: Special Muhurat session (18:15–19:15 IST, 13 slots) audited.
6. `test_intraday_scenario_6_holiday_excluded_from_expected_5m`: 2025-01-26 holiday excluded from slot expectations.
7. `test_intraday_scenario_7_valid_trading_day_included`: Regular business day 2025-01-27 generates 75 slots.
8. `test_intraday_scenario_8_duplicate_timestamps`: Duplicate timestamps flagged -> `duplicates = 1` -> `PARTIAL`.
9. `test_intraday_scenario_9_timezone_aware_timestamps`: `+05:30` localized timestamps normalized to IST string.
10. `test_intraday_scenario_10_timezone_naive_timestamps`: Naive timestamps interpreted strictly as IST local time.
11. `test_intraday_scenario_11_off_session_candles`: Candle at 08:00:00 IST flagged -> `off_session_records = 1` -> `PARTIAL`.
12. `test_intraday_scenario_12_future_dated_candles`: Future date timestamp flagged -> `freshness_status = "FUTURE_DATED"` -> `PARTIAL`.
