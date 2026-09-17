# TradeMind AI: Same-Bar Final Reconciliation

## 1. Ambiguity Reconciliation (N=50)
Resolved the percentage contradictions in previous audits:

| Population | Count | Ambiguity % | Status |
| :--- | :--- | :--- | :--- |
| **Total Historical Records** | 50 | 8.0% | Authoritative |
| **Price-Verified Sample** | 25 | **16.0%** | **RECONCILED** |
| **Data Missing/Unverified** | 25 | N/A | DATA_LIMITED |

## 2. Forensic Ambiguity Ledger
The following 4 signals hit both Target and Stop Loss within the same 1-day candle:
1. `sig_BRITANNIA_202608250436` (2026-09-02)
2. `sig_CUMMINSIND_202608241002` (2026-09-02)
3. `recon_ASTRAL_20260629_0` (2026-07-13)
4. `sig_ADANIGREEN_202608250435` (2026-08-26)

## 3. Impact Assessment
- **Methodology**: Strategy V2.2 currently resolves these using the closing state of the bar. 
- **Conservative Sensitivity**: Treating all 4 ambiguities as **Losses** results in an observed win rate of **51.0%** (N=49 binary outcomes).
- **Accounting Constraint**: Intrabar sequence for legacy records is unknown. **INTRABAR_AMBIGUOUS** label applied to the forensic metadata.

---
**Verdict**: **DATA_LIMITED**
16% of price-verified historical signals exhibit same-bar ambiguity. High-frequency intrabar data is required for definitive sequence resolution.
