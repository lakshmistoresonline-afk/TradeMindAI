# Data Pipeline Test Results

**Generated**: 2026-11-03  
**Status**: 100% PASS

## Automated Test Suite Summary

| Test Suite | Command | Total Tests | Passed | Failed | Duration |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Intraday Ingestion | `python -m pytest backend/tests/unit/test_intraday_ingestion.py -v` | 3 | 3 | 0 | 1.47s |
| Ingestion Pipeline | `python -m pytest backend/tests/unit/test_ingestion_pipeline.py -v` | 26 | 26 | 0 | 124.36s |
| Transaction Safety & Recovery | `python -m pytest backend/tests/unit/test_ingestion_transaction_safety.py -v` | 22 | 22 | 0 | 109.61s |
| Pulse Worker Lock | `python -m pytest backend/tests/unit/test_pulse_worker.py -v` | 6 | 6 | 0 | 17.32s |
| Full Backend Unit Suite | `python -m pytest backend/tests/unit/ -v` | 290 | 288 | 0 (2 skipped) | 195.08s |
| Git Whitespace Check | `git diff --check` | N/A | PASS | 0 | <1s |

## Key Verification Invariants

1. **Safety Invariants**:
   - `REAL_TRADING = False`
   - `LIVE_EXECUTION_ENABLED = False`
   - `BROKER_ORDER_EXECUTION_ENABLED = False`
   - `QUARANTINE_ACTIVE = True`

2. **Data Consistency**:
   - DuckDB `daily_ohlcv` vs Parquet value-level equality: **100% match across 499 listed equities** ($10^{-4}$ tolerance).
   - DuckDB `intraday_5m_ohlcv` vs Parquet `*_5m.parquet` 5m candles: **37,058 candles persisted across 498 distinct equities**.

3. **Global Validation Gate**:
   - `DataQualityService.evaluate_global_data_gate()`: **`PASS`**, `signal_generation_allowed: True`.
