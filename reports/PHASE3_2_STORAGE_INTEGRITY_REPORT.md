# Phase 3.2 Storage Integrity Report

**Date**: 2026-11-03  
**Evaluated Database**: `D:\TradeMindAI\backend\data\analytical.duckdb`  
**Evaluated Features Directory**: `D:\TradeMindAI\backend\data\features\`  
**Storage Consistency Pass Count**: `499` / 500  
**Unsupported Symbol**: `1` (`BAGMANE`)

## Consistency Audit Details

- **499 Listed Equities**: 100% DuckDB vs Parquet primary key and element-wise OHLCV value equality ($10^{-4}$ tolerance).
- **0 Value Mismatches**: Zero price or volume discrepancies between DuckDB `daily_ohlcv` / `intraday_5m_ohlcv` and corresponding Parquet files.
- **`BAGMANE` Unlisted Symbol**: Properly classified as `UNSUPPORTED`. Preserved in `reports/phase1_audit/BAGMANE_TRANSITION_RECONCILIATION.json`.
