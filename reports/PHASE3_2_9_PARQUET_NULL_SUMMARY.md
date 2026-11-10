# Phase 3.2.9 Parquet Null Summary Report

**Date**: 2026-11-03  
**Total Discovered Files**: 1,201 Parquet files across `backend/data/`  
**Null Analysis Source**: [reports/PHASE3_2_9_PARQUET_NULL_INVESTIGATION.csv](file:///D:/TradeMindAI/reports/PHASE3_2_9_PARQUET_NULL_INVESTIGATION.csv)

## Classification Breakdown

- **`READABLE_VALID`**: `1,006` files (0 NULLs in primary keys or OHLCV columns).
- **`READABLE_WITH_OHLCV_NULLS`**: `195` 5m intraday files (contain volume gap NULLs from Yahoo Finance provider quotes).
- **`READABLE_WITH_KEY_NULLS`**: `0` files (0 NULLs in primary `date` / `timestamp` keys).
- **`UNREADABLE`**: `0` files (100% of all 1,201 Parquet files are readable).
