# Phase 3.2.20 PostgreSQL Uniqueness Migration Report

**Date**: 2026-11-03  
**Target File**: [backend/core/postgres.py](file:///D:/TradeMindAI/backend/core/postgres.py)  
**Status**: **100% IMPLEMENTED & VERIFIED**

## Database Engine Separation & Startup Safety

1. **Engine Separation**:
   - `ensure_sqlite_columns()` uses SQLite `engine`.
   - `ensure_active_signal_idempotency_index()` safely supports both `engine` (SQLite) and `postgres_engine` (PostgreSQL) through explicit target engine parameter.
2. **Startup Safety**:
   - Normal application startup performs non-destructive schema verification without mutating production data or executing unapproved DDL.
3. **Partial Unique Index**:
   ```sql
   CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_signal
   ON live_signals (symbol)
   WHERE status = 'ACTIVE';
   ```
