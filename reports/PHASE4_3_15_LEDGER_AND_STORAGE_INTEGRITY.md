# Phase 4.3.15 Ledger and Storage Integrity Report

**Date**: 2026-11-03  
**Database**: `D:\TradeMindAI\backend\local_operational.db`  
**Classification**: **VERIFIED**

## Ledger Uniqueness & Storage Integrity

- **Database Partial Unique Index**: `idx_unique_active_signal` on `(symbol)` WHERE `status = 'ACTIVE'`.
- **Global Invariant**: Enforces at most 1 active signal per stock symbol globally.
- **DuckDB & Parquet Storage Integrity**: Non-destructive SQL upserts and cumulative Parquet dataset merging preserve historical candles.
