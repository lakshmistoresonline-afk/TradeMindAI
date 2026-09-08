# MARKET DATA QUALITY REPORT

## 1. Validation Gates
Every price point ingested must pass:
1. **Geometric Check**: price > 0.
2. **Temporal Check**: timestamp <= now.
3. **Identity Check**: symbol belongs to monitored universe.

## 2. Findings
- **Zero Fabrication**: Confirmed. Missing data remains NULL.
- **Sentinel Guard**: Confirmed. No -1.0 or 0.0 values found in the production Signal Ledger.
- **Freshness**: 100% of signals require data less than 15 minutes old for a `LIVE` classification.

---
**Status**: HIGH_FIDELITY.
