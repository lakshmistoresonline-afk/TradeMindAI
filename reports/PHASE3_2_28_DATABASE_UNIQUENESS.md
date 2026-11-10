# Phase 3.2.28 Database Uniqueness Report

**Date**: 2026-11-03  
**Target File**: [backend/core/postgres.py](file:///D:/TradeMindAI/backend/core/postgres.py)  
**Status**: **100% IMPLEMENTED & VERIFIED**

## Database-Level Global Active Signal Uniqueness

- **Partial Unique Index**: `idx_unique_active_signal` on `symbol` where `status == 'ACTIVE'`.
- **Invariant**: Enforces at most 1 active BUY signal per symbol globally across all timeframes and strategies.
- **Race Condition Handling**: `IntegrityError` rollback followed by active signal query returns `DUPLICATE_PREVENTED` cleanly.
