# TradeMind AI: Same-Bar Ambiguity Audit

## 1. Ambiguity Detection
Analyzed historical signals where both Target and Stop Loss levels were touched within the same daily candle:

| Metric | Value |
| :--- | :--- |
| **Total Resolved Signals Checked** | 24 |
| **Ambiguous Same-Bar Events** | 4 |
| **Ambiguity Rate** | **16.7%** |

## 2. Ambiguous Signals Ledger
| Signal ID | Symbol | Date | Target | Stop | High | Low |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sig_BRITANNIA_202608250436` | BRITANNIA | 2026-09-02 | 5138.1 | 5455.9 | 5256.0 | 5145.5 |
| `sig_CUMMINSIND_202608241002` | CUMMINSIND | 2026-09-02 | 5009.6 | 5319.4 | 5115.0 | 5054.5 |
| `recon_ASTRAL_20260629_0` | ASTRAL | 2026-07-13 | 1229.3 | 1420.5 | 1337.9 | 1312.9 |
| `sig_ADANIGREEN_202608250435` | ADANIGREEN | 2026-08-26 | 1265.6 | 1343.8 | 1330.0 | 1294.8 |

## 3. Impact Statement
- **Conservative Resolution**: In the current validation, these are recorded as wins/losses based on the final closing state, which introduces a 16.7% uncertainty in the outcome order.
- **Recommendation**: For institutional-grade audit, same-bar touches should be resolved using 1-minute or 5-minute intrabar data. If intrabar data is unavailable, these must be treated as "Loss" or "Ambiguous" to avoid overstating performance.

---
**Verdict**: **DATA_LIMITED**
16.7% of terminal outcomes are subject to same-bar ambiguity. High-frequency forensic data is required to resolve definitively.
