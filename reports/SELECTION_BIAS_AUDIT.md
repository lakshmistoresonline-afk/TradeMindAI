# TradeMind AI: Selection Bias Audit

## 1. The Selectivity Funnel
Evaluated the strategy's signal-emission filters to detect selection bias:

| Stage | Population | Selectivity % |
| :--- | :--- | :--- |
| **Market Scan** | 7,500 (Predictions) | 100% |
| **Emitted Signals** | 166 (Database) | **2.2%** |
| **Institutional Baseline** | 83 (Verified Audit) | 1.1% |
| **Active Signal Terminal** | 33 (Live UI) | 0.4% |

## 2. Decision Logic Integrity
- **Frozen Gates**: Signal Intelligence 4.0 uses a 120h Freshness Gate and a 1.0% Expected Value (EV) floor.
- **Probability Filter**: 100% of validated signals have `calibrated_probability > 0.52`.
- **Bias Confirmation**: The strategy is highly selective, meaning its reported performance (59% Win Rate) applies only to the "Top 1% of opportunities."

## 3. Findings
- **Valid Edge**: Selectivity is a core requirement of Strategy V2.2 and is not considered a defect. However, users must be aware that the system rejects 98.9% of candidate trades.
- **Distribution Stability**: Signal direction (UP/DOWN) in the 83-record set matches the 7500-record prediction distribution within a 5% margin, indicating no significant directional bias in selection.

---
**Verdict**: **PASS (Transparent)**
Selection bias is a documented and intentional design of the Strategy V2.2 risk layer.
