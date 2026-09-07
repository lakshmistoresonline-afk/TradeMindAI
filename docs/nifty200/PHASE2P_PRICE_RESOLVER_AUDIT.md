# PHASE 2P: PRICE RESOLVER AUDIT

## 1. Failover Orchestration
The `PriceResolver` has been hardened with deterministic failover sequences based on asset class.
-   **F&O Sequence**: Upstox -> Dhan -> Groww -> **DATA_UNAVAILABLE**.
-   **Equity Sequence**: Upstox -> Dhan -> Groww -> YFinance.

## 2. Anti-Contamination Verification
Verified that the system explicitly forbids `YFinanceProvider` from resolving F&O premiums. This ensures that underlying spot prices are never silently substituted for derivative current prices.

## 3. Sentinel Removal
Verified that `PriceResolver` no longer processes or accepts numeric markers (-1.0, -2.0) as valid prices. All failures result in `None`.

---
**Status**: RESOLVER_HARDENED.
