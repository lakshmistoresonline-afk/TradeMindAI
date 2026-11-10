# TradeMindAI — Phase A Historical OHLCV Report

**Service Component**: [backend/services/historical_backfill_service.py](file:///D:/TradeMindAI/backend/services/historical_backfill_service.py)  
**Historical Start Date**: `2015-01-01`  
**Price Adjustment Policy**: `auto_adjust = True` (Corporate-action split/bonus adjusted price basis)

---

## 1. Dynamic Completed Session As-Of Date Calculation

`HistoricalBackfillService.get_as_of_end_date()` dynamically computes the latest completed market session in `Asia/Kolkata` timezone:
- If current time is weekday before 15:30 IST, completed date is set to previous weekday.
- If current time is weekend, completed date rolls back to Friday.
- **Incomplete Session Guard**: Prevents incomplete active candles from entering historical daily storage.

---

## 2. Daily Bar Validation Rules

Function `HistoricalBackfillService.validate_historical_bar()` enforces strict bar-level quality rules:
1. **Incomplete Session Filter**: `date_obj <= as_of_end_dt`.
2. **Numeric Finiteness**: All numeric values (`Open`, `High`, `Low`, `Close`, `Volume`) must satisfy `np.isfinite()`.
3. **Positive Price Contract**: `Open > 0`, `High > 0`, `Low > 0`, `Close > 0`.
4. **Non-Negative Volume Contract**: `Volume >= 0`. Rejects negative volume without silent coercion to zero (`NEGATIVE_VOLUME`).
5. **OHLC Geometry Contract**:
   - `High >= Low`
   - `High >= Open`
   - `High >= Close`
   - `Low <= Open`
   - `Low <= Close`

---

## 3. Rejection Audit & Gap Tracking

Function `fetch_authentic_source_bars_with_audit()` returns structured rejection metadata `(valid_bars, rejected_records)` containing symbol, date, and rejection reason. Rejections are logged and stored in the ingestion audit trail.

---

## 4. Test Execution Evidence

- `test_phase_a_historical_ohlcv_bar_validation_valid`: **PASSED**
- `test_phase_a_historical_ohlcv_nan_inf_rejected`: **PASSED**
- `test_phase_a_historical_ohlcv_geometry_violation_rejected`: **PASSED**
- `test_phase_a_historical_ohlcv_negative_volume_rejected`: **PASSED**
- `test_phase_a_historical_incomplete_session_filtered`: **PASSED**
