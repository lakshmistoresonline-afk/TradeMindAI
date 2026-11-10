# Phase 4.3.3 Strategy Input Source Trace Report

**Date**: 2026-11-03  
**Status**: **VERIFIED**

## Strategy Input Requirements

- **SHORT**: Requires 5m intraday OHLCV bars. Returns `INSUFFICIENT_INTRADAY_DATA` if missing.
- **SWING**: Requires daily OHLCV + 5m intraday OHLCV bars with 200-bar warm-up history.
- **LONG**: Requires daily OHLCV bars with 200-bar warm-up history.
- **Time Safety**: `evaluation_timestamp` cutoff enforced across all feature vectors (`date <= eval_time`).
