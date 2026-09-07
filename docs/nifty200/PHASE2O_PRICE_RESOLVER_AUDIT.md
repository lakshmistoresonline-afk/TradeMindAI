# PHASE 2O: PRICE RESOLVER AUDIT

## 1. Failure Sequence Verification
The `PriceResolver` has been hardened with a dedicated F&O failover sequence.
- **F&O Flow**: Upstox -> Dhan -> Groww -> **DATA_UNAVAILABLE**.
- **Equity Flow**: Upstox -> Dhan -> Groww -> YFinance.

## 2. Anti-Contamination Check
Verified that `PriceResolver` strictly prevents YFinance from being used as a source for F&O premiums.

---
**Status**: RESOLVER_HARDENED.
