# Phase 3.2.2 Intraday Regression Test Report

**Date**: 2026-11-03  
**Executable Scenarios**: 12/12  
**Test File**: [backend/tests/unit/test_data_quality_gate.py](file:///D:/TradeMindAI/backend/tests/unit/test_data_quality_gate.py)  
**Status**: **100% PASSED** (24 total unit tests)

## 12 Executable Test Scenario Results

| Scenario ID | Test Name | Assertion | Result |
| :--- | :--- | :--- | :---: |
| **S1** | `test_intraday_scenario_1_complete_valid_session` | 75 valid slots -> `missing_intervals = 0` | **PASS** |
| **S2** | `test_intraday_scenario_2_one_missing_5m_candle` | 74 valid slots -> `missing_intervals = 1` -> PARTIAL | **PASS** |
| **S3** | `test_intraday_scenario_3_multiple_missing_5m_candles` | 65 valid slots -> `missing_intervals = 10` -> PARTIAL | **PASS** |
| **S4** | `test_intraday_scenario_4_entirely_missing_trading_session` | 0 candles -> `missing_intervals = 75` -> PARTIAL | **PASS** |
| **S5** | `test_intraday_scenario_5_special_session_muhurat` | Evening session 18:15–19:15 IST (13 slots) | **PASS** |
| **S6** | `test_intraday_scenario_6_holiday_excluded_from_expected_5m` | 2025-01-26 excluded from slot expectations | **PASS** |
| **S7** | `test_intraday_scenario_7_valid_trading_day_included` | 2025-01-27 generates 75 expected slots | **PASS** |
| **S8** | `test_intraday_scenario_8_duplicate_timestamps` | Duplicate timestamp flagged -> PARTIAL | **PASS** |
| **S9** | `test_intraday_scenario_9_timezone_aware_timestamps` | ISO offset normalized to `Asia/Kolkata` string | **PASS** |
| **S10** | `test_intraday_scenario_10_timezone_naive_timestamps` | Naive timestamps interpreted as local IST | **PASS** |
| **S11** | `test_intraday_scenario_11_off_session_candles` | 08:00:00 IST candle flagged -> PARTIAL | **PASS** |
| **S12** | `test_intraday_scenario_12_future_dated_candles` | Future date flagged -> `FUTURE_DATED` -> PARTIAL | **PASS** |
