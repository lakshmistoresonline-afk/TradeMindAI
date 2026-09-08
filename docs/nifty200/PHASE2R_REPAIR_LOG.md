# TRADEMIND AI: PHASE 2R — REPAIR LOG

## 1. Adapter Sanitization
- **Problem**: Provider adapters used numeric error markers (-1.0) in price fields.
- **Fix**: Replaced all numeric sentinels with `None` (NULL) in `UpstoxProvider.get_ltp` and `DhanProvider.get_ltp`.
- **Status**: **RESOLVED**.

## 2. Failover Sequence Logic
- **Problem**: Primary/Secondary resolution was not distinguishing between Equity and F&O sequences.
- **Fix**: Hardened `PriceResolver` to skip YFinance for derivatives while preserving it for equity.
- **Status**: **RESOLVED**.

---
**Status**: RECTIFIED.
