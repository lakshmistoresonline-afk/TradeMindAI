# TRADEMIND AI: PHASE 2T — REPAIR LOG

## 1. Sentinel Removal (Objective 2)
- **Problem**: Leftover numeric error markers (-1.0, -2.0) were identified in the Upstox and Dhan adapters.
- **Fix**: Replaced all numeric status codes with `None` and mapped failure details to the `price_status` column.
- **Result**: Certification engine now correctly identifies `CONFIGURATION_REQUIRED`.

## 2. Failover Sequence Logic
- **Problem**: Resolution sequence did not enforce F&O-only routing.
- **Fix**: Hardened `PriceResolver` to skip YFinance for derivatives while preserving it for equity.
- **Status**: **RESOLVED**.

---
**Status**: RECTIFIED.
