# PHASE 2O: FAILOVER TEST REPORT

## 1. Simulation: Primary Auth Failure
- **Action**: Attempt LTP retrieval for `RELIANCE` (Equity).
- **Primary (Upstox)**: `AUTH_REQUIRED`.
- **Secondary (Dhan)**: `AUTH_REQUIRED`.
- **Fallback (YFinance)**: **SUCCESS** (1309.20).
- **Result**: Failover logic confirmed for Equity.

## 2. Simulation: F&O Blocker
- **Action**: Attempt LTP for `RELIANCE3100CE`.
- **Primary/Secondary**: `AUTH_REQUIRED`.
- **YFinance**: **SKIPPED** (F&O Forbidden).
- **Result**: `DATA_UNAVAILABLE`. **PASS**.

---
**Verdict**: Failover Safety Verified.
