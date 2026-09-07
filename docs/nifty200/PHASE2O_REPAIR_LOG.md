# PHASE 2O: REPAIR LOG

## 1. Provider Adapter Rectification
- **Problem**: Adapters returned 0.0 on failure, violating institutional truth rules.
- **Fix**: Replaced 0.0 with explicit error markers (-1.0 for Auth, -2.0 for missing instrument).
- **Result**: Certification engine now correctly identifies `CONFIGURATION_REQUIRED`.

## 2. Failover Sequence Repair
- **Problem**: `PriceResolver` did not distinguish between Equity and F&O sequences.
- **Fix**: Implemented strict `FNO_SEQUENCE` that forbids YFinance usage for derivatives.

---
**Status**: REPAIRED.
