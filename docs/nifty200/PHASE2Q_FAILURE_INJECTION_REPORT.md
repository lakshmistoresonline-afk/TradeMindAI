# PHASE 2Q: FAILURE INJECTION REPORT

## 1. Test: Numeric Sentinel Guard
- **Action**: Injected -1.0 as a mock LTP.
- **Detector**: `PriceResolver` price-range check.
- **Result**: `FAIL` correctly identified. System rejected the sentinel. **PASS**.

## 2. Test: Identity Contamination
- **Action**: Underlying spot price assigned to `derivative_current`.
- **Result**: Blocked by the `IDENTITY_MISMATCH` check. **PASS**.

## 3. Test: Ambiguous Match
- **Action**: Attempt resolution for an instrument with duplicate IDs in Neon.
- **Result**: Correctly marked as `AMBIGUOUS` by the master service. **PASS**.

---
**Verdict**: Institutional defensive logic verified.
