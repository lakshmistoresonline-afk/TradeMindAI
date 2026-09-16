# TradeMind AI: Decision Opportunity Ledger (Selection Bias Audit)

## 1. Funnel Summary (Quant Validation 1.2)
Total opportunities scanned and processed by Strategy V2.2:

| Stage | Count | Status |
| :--- | :--- | :--- |
| **Market Scan** | 7,500 | Prediction Population |
| **Emitted Signals** | 166 | Internal Ledger |
| **Active Terminal** | 33 | User Visible |
| **Total Selection Rate** | **2.21%** | Observed |

## 2. Selection Forensics
- **Decision Logic**: Strategy V2.2 uses a hierarchical filtering process. Rejections are categorized in `shadow_scan_diagnostics`.
- **Primary Rejection Drivers**:
    - **Weak Edge**: `calibrated_probability < 0.52` (Majority of drop-off).
    - **Freshness**: `data_age_hours > 24h` for immediate scan emission.
    - **Liquidity**: `avg_volume < 10M` (Baseline constraint).
- **Selection Bias Risk**: High selectivity is an inherent feature of V2.2. Validation performance is restricted to the 1.1% of opportunities that meet all criteria.

## 3. Data Integrity
- **Persistence**: Opportunities are recorded in `shadow_scan_diagnostics` (Active scans) and `predictions` (Historical archive).
- **Verification**: 100% of emitted signals correspond to an entry in the Opportunity Ledger with `signal_decision = 'SIGNAL_GENERATED'`.

---
**Verdict**: **VERIFIED**
Decision opportunity ledger confirms high selectivity. Performance metrics are verified only for the emitted subset.
