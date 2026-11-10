# Phase 4.3.2 Strategy Input Source Trace Report

**Date**: 2026-11-03  
**Status**: **VERIFIED SOURCE TRACE**

## Execution Path & Data Contract

1. **Market Data Retrieval**: `DuckDB` (`daily_ohlcv`, `intraday_5m_ohlcv`) & `Parquet` feature storage (`backend/data/features/*.parquet`).
2. **Feature Builder**: `EquitySignalGenerationService.build_feature_vector()` builds `OHLCV`, `ATR`, `RSI`, `ema_20`, `ema_50`, `ema_200`, `sma_20` with 200-bar EMA warm-up.
3. **Signal Generation Engine**: `SignalEngine.generate_signal()` checks direction (`LONG`), ML predictions (`UP`), regime, risk parameters, and expected value (`EV`).
