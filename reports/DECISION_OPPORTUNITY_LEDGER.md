# TradeMind AI: Decision Opportunity Ledger (Selection Bias Audit)

## 1. Funnel Summary (Quant Validation 1.1)
Total opportunities scanned and processed by Strategy V2.2:

| Stage | Count | Action |
| :--- | :--- | :--- |
| **Scanned Opportunities** | 7500 | Prediction Generated |
| **Signal Emitted** | 166 | Signal Ledger Entry |
| **Active Terminal** | 33 | User Visible |
| **Total Selection Rate** | **2.21%** | (High Selectivity) |

## 2. Prediction Distribution (N=7500)
| Direction | Count | Percentage |
| :--- | :--- | :--- |
| **UP** | 3829 | 51.05% |
| **DOWN** | 2532 | 33.76% |
| **NEUTRAL** | 1139 | 15.19% |

## 3. Rejection Root Causes (Heuristic)
Based on funnel drop-off (7334 rejected opportunities):
- **Probability Filter**: Majority of rejections occur when `calibrated_probability < 0.60`.
- **EV Filter**: Rejection if `expected_value < 1.0%`.
- **Regime Alignment**: Rejection if direction is counter to market regime.
- **Risk/Atr Gate**: Rejection if Stop Loss distance exceeds portfolio constraints.

## 4. Selection Bias Statement
The strategy is highly selective (2.2%). Reported performance metrics are based only on signals that passed all V2.2 quality gates. This is correct behavior for a trading system, but implies that the model's aggregate accuracy on the "Total Funnel" (7500) would be lower than the reported Signal Win Rate (59%).

---
**Verdict**: **VERIFIED**
Decision opportunity ledger confirms high selectivity and legitimate filter composing.
