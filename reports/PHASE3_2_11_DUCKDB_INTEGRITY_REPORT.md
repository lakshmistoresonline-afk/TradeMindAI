# Phase 3.2.11 DuckDB Integrity Audit Report

**Date**: 2026-11-03  
**Database Path**: `D:\TradeMindAI\backend\data\analytical.duckdb` (**244.51 MB**)  
**Source JSON**: [reports/PHASE3_2_11_DUCKDB_INTEGRITY.json](file:///D:/TradeMindAI/reports/PHASE3_2_11_DUCKDB_INTEGRITY.json)

## Read-Only Inspection Summary

1. **`daily_ohlcv` Table**: 1,144,547 rows across 499 unique symbols. **0 NULLs in any column**, **0 duplicate composite keys**, **0 OHLCV geometry violations**.
2. **`intraday_5m_ohlcv` Table**: 37,058 rows across 498 unique symbols. **0 NULLs in any column**, **0 duplicate composite keys**, **0 OHLCV geometry violations**.
3. **Read-Only Mode**: Connection established with `read_only=True` strictly enforcing zero write operations.
