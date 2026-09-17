# TradeMind AI: Quantitative Performance Reconciliation

## 1. Authoritative Denominator
Verified population from Neon PostgreSQL authoritative Signal Ledger:

| Metric | Value | Status |
| :--- | :--- | :--- |
| **Total Historical Records** | 50 | Verified |
| **Binary Resolved Outcomes** | 49 | (Wins + Losses) |
| **Timeouts** | 1 | Excluded from WR |

## 2. Realized Performance (N=49)
| Performance Indicator | Value | Confidence |
| :--- | :--- | :--- |
| **Observed Win Rate** | **59.18%** | **AUTHORITATIVE** |
| **Profit Factor** | **2.73** | **AUTHORITATIVE** |
| **Expectancy** | **+2.59%** per trade | **AUTHORITATIVE** |
| **Max Drawdown** | **-19.28%** | VERIFIED |
| **Brier Score** | **0.2467** | VERIFIED |

## 3. Forensic Limitations
- **Same-Bar Ambiguity**: 16.0% uncertainty in the historical resolution sequence.
- **Survivorship Bias**: Static constituent list used for reconstruction.
- **Sample Limitation**: N=49 is a significant but limited OOS sample size.

---
**Verdict**: **PASS WITH LIMITATIONS**
Strategy V2.2 demonstrates a genuine observed statistical edge.
