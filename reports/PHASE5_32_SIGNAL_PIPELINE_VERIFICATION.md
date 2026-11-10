# TradeMindAI — Phase 5.32 Signal Pipeline Verification Report

## 1. Production Signal Pipeline Execution Results

- **DuckDB Feature Builder Integration**: Verified in `test_phase5_genuine_signal_pipeline_end_to_end_proof()` with 205 OHLCV candles, 200-bar EMA warm-up, ATR, and RSI calculation.
- **Model Registry Lookup**: Verified exact matching by symbol and horizon (`INFY` / `SWING`).
- **Quality Gate & Risk Validation**: Verified fail-closed behavior on quality score and risk geometry failures.
