# NIFTY-200 EQUITY SIGNAL REPAIR LOG

## 1. Look-ahead Verification Hardening
- **Problem**: DuckDB indicators were not explicitly checked for causal ordering against signal timestamps.
- **Fix**: Added a `temporal_guard` in the `SignalEngine` to verify that no market data point used for features is timestamped after the signal creation.

## 2. Universe Count Correction
- **Problem**: Database contained 210 stocks under `NIFTY_200` membership due to overlapping rebalancing events.
- **Fix**: Re-synced the `UniverseService` with the absolute `NIFTY_200_AUG2026` canonical list. Redundant entries were decommissioned.

## 3. P&L Precision Fix
- **Problem**: Net P&L calculations showed minor floating-point drift in certain terminal hits.
- **Fix**: Enforced a `round(x, 2)` policy in the `OutcomeEngine` for all institutional cost deductions.

---
**Status**: RECTIFIED.
