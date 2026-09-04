# TRADEMIND AI: PROBABILITY CALIBRATION REPORT (V2)

## 1. Reliability Audit (n=50 Verified)
| Bucket | Count | Avg Pred Prob | Actual Win Rate | Status |
| :--- | :--- | :--- | :--- | :--- |
| **0.00 – 0.52** | 35 | 48.4% | 46.7% | **WELL CALIBRATED** |
| **0.52 – 0.70** | 0 | 0.0% | 0.0% | **NO DATA** |
| **0.70 – 1.00** | 15 | 75.0% | 60.0% | **UNDERPERFORMING** |

## 2. Calibration Metrics
- **Brier Score**: 0.2140
- **Log Loss**: 0.6235
- **ROC-AUC**: 0.605 (Model Classification)

## 3. Findings
The model is well-calibrated for low-confidence signals but tends to be overly optimistic in high-confidence scenarios. This indicates a potential "Alpha Compression" effect where high-probability signals are triggering in late-trend environments.

## 4. Constraint
Strategy V2.2 remains **FROZEN**. No recalibration has been performed.
