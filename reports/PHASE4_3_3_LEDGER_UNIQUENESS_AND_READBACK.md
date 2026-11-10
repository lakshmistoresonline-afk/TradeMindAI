# Phase 4.3.3 Ledger Uniqueness & Readback Report

**Date**: 2026-11-03  
**Database File**: `backend/local_operational.db` (`live_signals` table)  
**Status**: **VERIFIED**

## Ledger Uniqueness & Persistence Verification

- **Database Partial Unique Index**: `idx_unique_active_signal` on `(symbol)` WHERE `status = 'ACTIVE'`.
- **Global Invariant**: Enforces at most 1 active signal per stock symbol globally.
- **Independent Read-Back**: Tested and verified in `test_end_to_end_controlled_signal_persistence_and_readback()`.
