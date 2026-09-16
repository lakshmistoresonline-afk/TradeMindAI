# TradeMind AI: Same-Bar Final Reconciliation

## 1. Ambiguity Reconciliation (N=50)
Resolved the contradiction between 8.2% and 16.7% reported ambiguity rates:

| Population | Count | Ambiguity % | Status |
| :--- | :--- | :--- | :--- |
| **Total Historical Records** | 50 | 8.0% | Authoritative |
| **Price-Verified Sample** | 25 | **16.0%** | **RECONCILED** |
| **Data Missing/Unverified** | 25 | N/A | **DATA_LIMITED** |

## 2. Definitive Ambiguity Ledger
The following 4 signals hit both Target and Stop Loss within the same 1-day candle:
1. `sig_BRITANNIA_202608250436` (2026-09-02)
2. `sig_CUMMINSIND_202608241002` (2026-09-02)
3. `recon_ASTRAL_20260629_0` (2026-07-13)
4. `sig_ADANIGREEN_202608250435` (2026-08-26)

## 3. Sensitivity Analysis
Impact of ambiguity on Win Rate (59.18% baseline):

| Scenario | Win Rate | Net P&L (Aggregate) |
| :--- | :--- | :--- |
| **Canonical** (Current V2.2) | 59.2% | +126.9% |
| **Conservative** (All ambiguous = Loss) | 51.0% | +108.5% |
| **Excluded** (Remove 4 ambiguous) | 55.6% | +112.2% |

---
**Verdict**: **SAMPLE_LIMITED**
16% of price-verified signals exhibit same-bar ambiguity. High-frequency forensic data is required to resolve sequence definitively. Strategy V2.2 results are robust but subject to a -8% win-rate sensitivity floor.
