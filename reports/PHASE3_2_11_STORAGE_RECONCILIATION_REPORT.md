# Phase 3.2.11 Storage Reconciliation Report

**Date**: 2026-11-03  
**Database Path**: `D:\TradeMindAI\backend\data\analytical.duckdb`  
**Features Path**: `D:\TradeMindAI\backend\data\features\`  
**Daily Source CSV**: [reports/PHASE3_2_11_DAILY_STORAGE_RECONCILIATION.csv](file:///D:/TradeMindAI/reports/PHASE3_2_11_DAILY_STORAGE_RECONCILIATION.csv)  
**Intraday Source CSV**: [reports/PHASE3_2_11_INTRADAY_STORAGE_RECONCILIATION.csv](file:///D:/TradeMindAI/reports/PHASE3_2_11_INTRADAY_STORAGE_RECONCILIATION.csv)

## Storage Summary Breakdown

- **Daily Storage**: `499` `EXACT_MATCH` (100% key and value equality with `max_absolute_ohlcv_diff = 0.0`), `1` `UNSUPPORTED_PENDING_EVIDENCE` (`BAGMANE`), `0` mismatches.
- **Intraday Storage**: `498` `EXACT_MATCH` (100% key and value equality with `max_absolute_ohlcv_diff = 0.0`), `1` `INTRADAY_PARQUET_MISSING` (`ICICIPRULI`), `1` `UNSUPPORTED_PENDING_EVIDENCE` (`BAGMANE`), `0` mismatches.
