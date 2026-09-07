# PHASE 2N: PROVIDER FAILOVER TEST REPORT

## 1. Simulated Scenarios
- **Scenario A**: Primary (Upstox) unauthenticated.
- **Scenario B**: Primary (Upstox) timeout.
- **Scenario C**: F&O Pricing available via Primary vs Secondary.

## 2. Evidence (Scenario A)
- **Signal**: `sig_RELIANCE_...` (Equity)
- **Action**: Call `PriceResolver.resolve_current_price()`.
- **Trace**:
    1. Check Upstox -> `AUTH_REQUIRED`.
    2. Check Dhan -> `AUTH_REQUIRED`.
    3. Check YFinance -> **SUCCESS**.
- **Result**: `YFinanceProvider` correctly took over the Equity resolution.

## 3. Evidence (F&O Failure Injection)
- **Signal**: `SBIN860CE` (Option)
- **Action**: Attempt resolution.
- **Trace**: All 3 providers failed (Auth or Capability).
- **Result**: `DATA_UNAVAILABLE`. **PASS**. (Correct behavior: never substitute spot for premium).

---
**Verdict**: Failover logic is mathematically deterministic and forensically safe.
