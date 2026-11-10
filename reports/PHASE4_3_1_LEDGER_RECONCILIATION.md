# Phase 4.3.1 Signal Ledger Reconciliation Report

**Date**: 2026-11-03  
**Database File**: `backend/local_operational.db` (`live_signals` table)  
**Status**: **RECONCILED & VERIFIED**

## Ledger Counts & State Machine Breakdown

- **Total Signals in Operational Ledger**: **489 Signals**
- **Distinct Stock Symbols Represented**: **119 Equities**
- **Breakdown by Status**:
  - `WAITING_FOR_ENTRY`: **488 signals** (Pending limit entry price hit)
  - `ACTIVE`: **1 signal** (`HDFCBANK`)
- **Breakdown by Timeframe**:
  - `SHORT`: **236 signals**
  - `SWING`: **189 signals**
  - `LONG`: **64 signals**
- **Signal Direction & Rating**: 100% `LONG` / `BUY`
