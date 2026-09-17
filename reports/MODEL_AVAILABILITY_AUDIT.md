# TradeMind AI: Model Availability Audit

## 1. Symbol-Level Coverage (V2.2 Champion Model)
Verified prediction availability across the NIFTY-200 universe (Target: 500 scans/symbol):

| Rank | Symbol | Prediction Count | Coverage % | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | RELIANCE | 2119 | 100% | **AUTHORITATIVE** |
| 2 | ACC | 1300 | 100% | **AUTHORITATIVE** |
| 3 | TCS | 936 | 100% | **AUTHORITATIVE** |
| 4 | INFY | 364 | 72.8% | **VERIFIED** |
| 5 | ICICIBANK | 249 | 49.8% | DATA-LIMITED |
| ... | ... | ... | ... | ... |
| 200 | NYKAA | 1 | 0.2% | DATA-LIMITED |

Full matrix available in `reports/MODEL_COVERAGE_MATRIX_V22.csv`.

## 2. Findings
- **Data Skew**: Validation results are dominated by a handful of high-availability symbols (Top 3 account for 58% of all predictions).
- **Uniformity Violation**: Performance cannot be claimed as uniform across the NIFTY-200 universe. Strategy V2.2 exhibits an "Availability Bias" toward large-cap symbols with deep history.
- **Data Gaps**: 124/202 symbols have < 10% coverage, indicating significant periods where no machine decisions were possible.

---
**Verdict**: **DATA_LIMITED**
Predictive edge is verified primarily on the high-coverage subset (NIFTY-50 equivalent). Broad-market validation is sample-limited.
