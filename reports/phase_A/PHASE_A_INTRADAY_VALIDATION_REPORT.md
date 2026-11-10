# TradeMindAI — Phase A Intraday Validation Report

**Service Component**: [backend/services/intraday_ingestion_service.py](file:///D:/TradeMindAI/backend/services/intraday_ingestion_service.py)  
**Timeframe**: `5-minute (5m)`  
**Timezone**: `Asia/Kolkata (IST)`

---

## 1. Intraday Validation Rules

1. **Timezone Normalization**: Normalizes naive timestamps to `Asia/Kolkata` and converts timezone-aware timestamps safely.
2. **5-Minute Alignment**: Requires `minute % 5 == 0` and `second == 0`.
3. **Session Hours Enforcement**:
   - Regular Sessions: `09:15:00` to `15:25:00` IST.
   - Special Sessions (Muhurat Trading): `18:15:00` to `19:15:00` IST.
4. **Duplicate & Future Filter**: Rejects duplicate timestamps (`keep='last'`) and future-dated timestamps (`dt > now_kolkata`).
5. **Numeric Finiteness**: All 5 columns (`Open`, `High`, `Low`, `Close`, `Volume`) must be finite (`np.isfinite()`).
6. **Price & Volume Contract**: `Open > 0`, `High > 0`, `Low > 0`, `Close > 0`, `Volume >= 0`.
7. **OHLC Geometry Contract**: `High >= Low`, `High >= Open`, `High >= Close`, `Low <= Open`, `Low <= Close`.

---

## 2. Session-Aware Expected Slot Generation

Function `generate_expected_5m_slots(date_str: str)` in `DataQualityService` generates expected 5-minute slots:
- **Regular Session**: 75 slots (`09:15:00` to `15:25:00` IST).
- **Muhurat Session**: 13 slots (`18:15:00` to `19:15:00` IST).

---

## 3. Independent Missing Interval Calculation

Missing 5m intervals are calculated independently from business trading days (`expected_5m_trading_days`) derived from `VERSIONED_NSE_TRADING_CALENDAR_V1`, excluding exchange holidays:
`missing_5m_set = expected_5m_set - observed_5m_set`

This ensures that missing entire trading sessions as well as individual missing 5m candles are accurately detected.

---

## 4. Test Verification Summary

- `test_phase_a_expected_5m_slots_regular_vs_muhurat`: **PASSED**
- `test_intraday_scenario_1_complete_valid_session`: **PASSED**
- `test_intraday_scenario_2_one_missing_5m_candle`: **PASSED**
- `test_intraday_scenario_3_multiple_missing_5m_candles`: **PASSED**
- `test_intraday_scenario_4_entirely_missing_trading_session`: **PASSED**
- `test_intraday_scenario_5_special_session_muhurat`: **PASSED**
- `test_intraday_scenario_6_holiday_excluded_from_expected_5m`: **PASSED**
- `test_intraday_scenario_8_duplicate_timestamps`: **PASSED**
- `test_intraday_scenario_9_timezone_aware_timestamps`: **PASSED**
- `test_intraday_scenario_10_timezone_naive_timestamps`: **PASSED**
- `test_intraday_scenario_11_off_session_candles`: **PASSED**
- `test_intraday_scenario_12_future_dated_candles`: **PASSED**
