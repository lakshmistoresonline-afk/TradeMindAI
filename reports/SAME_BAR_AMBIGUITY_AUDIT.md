# TradeMind AI: Same-Bar Ambiguity Audit

## 1. Ambiguity Detection (Population N=50)
Analyzed terminal outcomes where both Target and Stop Loss levels were touched within the same daily candle:

| Metric | Value | Status |
| :--- | :--- | :--- |
| **Total Resolved Signals Audited** | 49 | Authoritative |
| **Ambiguous Same-Bar Events** | 4 | **OBSERVED** |
| **Ambiguity Rate** | **8.2%** | **SAMPLE_LIMITED** |

## 2. Identified Ambiguities
The following signals are subject to resolution uncertainty:
- `sig_BRITANNIA_202608250436` (2026-09-02)
- `sig_CUMMINSIND_202608241002` (2026-09-02)
- `recon_ASTRAL_20260629_0` (2026-07-13)
- `sig_ADANIGREEN_202608250435` (2026-08-26)

## 3. Impact Statement
- **Accounting Uncertainty**: An 8.2% ambiguity rate implies that approximately 4 outcomes could be incorrectly classified (e.g., a "Win" that was actually hit *after* a "Stop" was touched).
- **Conservatism**: Strategy V2.2 currently resolves these based on the closing state of the bar. For a "Hardened" verdict, these should be treated as losses to establish a worst-case performance floor.

---
**Verdict**: **SAMPLE_LIMITED**
Resolution of same-bar collisions requires high-frequency intrabar data not currently present in the Neon database.
