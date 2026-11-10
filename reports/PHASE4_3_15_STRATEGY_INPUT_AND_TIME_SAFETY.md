# Phase 4.3.15 Strategy Input and Time Safety Report

**Date**: 2026-11-03  
**Classification**: **VERIFIED TIME-SAFE**

## Strategy Input & Time Safety Controls

- **SHORT**: Requires 5m intraday OHLCV bars. Fails closed with `INSUFFICIENT_INTRADAY_DATA` when missing.
- **SWING**: Requires daily OHLCV + 5m intraday OHLCV bars with 200-bar EMA warm-up.
- **LONG**: Requires daily OHLCV bars with 200-bar EMA warm-up.
- **Time Safety**: `evaluation_timestamp` cutoff enforced across all feature vectors (`date <= eval_time`).
