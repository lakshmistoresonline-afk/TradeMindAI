# Phase 4.3.12 Ledger Integrity Report

**Date**: 2026-11-03  
**Database**: `D:\TradeMindAI\backend\local_operational.db`  
**Classification**: **VERIFIED**

## Ledger Uniqueness & Persistence Verification

- **Database Partial Unique Index**: `idx_unique_active_signal` on `(symbol)` WHERE `status = 'ACTIVE'`.
- **Global Invariant**: Enforces at most 1 active signal per stock symbol globally.
- **Independent Read-Back**: Tested and verified in `test_genuine_signal_pipeline_end_to_end_proof()`.
