# TRADEMIND AI: PHASE 2Q — REPAIR LOG

## 1. Instrument Master Finalization
- **Problem**: `InstrumentMasterService` lacked actual SQL queries for precision matching.
- **Fix**: Implemented complete 6-tier matching (Underlying, Expiry, Strike, etc.) using SQLAlchemy and the Neon `instruments` table.

## 2. Removed Hidden Sentinels
- **Problem**: Code audit revealed leftover `-1.0` and `-2.0` return values in the Upstox adapter.
- **Fix**: Replaced all numeric error sentinels with `None` to satisfy the institutional "Zero Fabrication" mandate.

## 3. Failover Orchestration
- **Problem**: System was attempting to fall back to YFinance for F&O premiums.
- **Fix**: Hardened the `PriceResolver` to skip YFinance for any derivative resolution attempt.

---
**Status**: RECTIFIED.
