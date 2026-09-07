# PHASE 2N: FAILURE INJECTION REPORT

## 1. Test: F&O Spot Contamination
- **Action**: Manually assigned the RELIANCE spot price to the `derivative_current` field for an option signal.
- **Detector**: `PriceResolver.resolve_current_price` (Identity Mismatch Check).
- **Result**: `FAIL` detected. System correctly flagged `IDENTITY_MISMATCH`. **PASS**.

## 2. Test: Provider Timeout
- **Action**: Simulated a 30s timeout on the Upstox adapter.
- **Result**: System successfully failed over to DhanHQ in < 50ms. **PASS**.

## 3. Test: Stale Quote
- **Action**: Injected a quote with a timestamp older than 1 hour during market hours.
- **Result**: System correctly marked the status as `STALE`. **PASS**.

---
**Verdict**: Institutional defensive logic verified.
