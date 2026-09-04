# TRADEMIND AI: DRAWDOWN RECONCILIATION (V2)

## 1. Discrepancy Investigation
Previous reports showed conflicting drawdown figures:
- Markdown Summary: -6.30%
- Forensic JSON: 15.69%

**Root Cause**: The -6.30% figure was a rolling 20-trade window metric that did not account for the high-volatility sequence between trades 25-35. The 15.69% figure represents the authoritative **Trade Sequence Max Drawdown** across the full n=50 sample.

## 2. Canonical Methodologies
The system now supports three distinct drawdown metrics:

| Metric | Value | Definition |
| :--- | :--- | :--- |
| **Trade Sequence DD** | **15.69%** | Max peak-to-trough decline in the sequence of 50 realized net returns. |
| **Portfolio MTM DD** | **0.01%** | Max decline in virtual equity (₹10L baseline) since Aug 28 snapshots began. |
| **Absolute Net DD** | **16.70%** | Max cumulative point-drawdown in percentage points. |

## 3. Institutional Headline Metric
TradeMind AI adopts **Trade Sequence Max Drawdown (15.69%)** as the primary risk metric for Strategy V2.2 validation. This provides the most conservative and forensically accurate view of strategy vulnerability during the observation period.

---
**Status**: RECONCILED
