# Phase 4.3.2 Ledger Schema and Uniqueness Report

**Date**: 2026-11-03  
**Database File**: `backend/local_operational.db` (`live_signals` table)  
**Status**: **VERIFIED**

## Ledger Uniqueness & State Machine

- **Database-Level Partial Unique Index**: `idx_unique_active_signal` on `(symbol)` WHERE `status = 'ACTIVE'`.
- **Global Invariant**: Enforces at most 1 active signal per stock symbol globally.
- **State Machine**:
  - `WAITING_FOR_ENTRY`: Initial state when signal is created waiting for limit entry price.
  - `ACTIVE`: Activated state when live price hits entry zone (`HDFCBANK`).
