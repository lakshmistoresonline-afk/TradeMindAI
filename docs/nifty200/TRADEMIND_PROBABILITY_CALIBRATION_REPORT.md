# TRADEMIND AI: PROBABILITY CALIBRATION REPORT

## 1. Methodology: Platt Scaling
The system uses **Platt Scaling** (Sigmoid transformation) to convert raw Random Forest outputs into calibrated probabilities.
- **Calibration Set**: Chronological middle 20% of the dataset.
- **Validation Set**: Latest 20% (Out-of-sample).

## 2. Calibration Metrics
- **Brier Score**: Primary metric for probability accuracy (Lower is better).
- **Log Loss**: Measures the uncertainty and penalty for incorrect confident predictions.
- **Reliability Curve**: Mapping of Predicted Probability vs. Actual Win Frequency.

## 3. Current Strategy V2.2 Performance (n=20)
| Bucket | Pred. Prob | Actual WR | Status |
| :--- | :--- | :--- | :--- |
| (0.00, 0.52] | 48.44% | 46.67% | **WELL CALIBRATED** |
| (0.52, 0.70] | 0.00% | 0.00% | NO DATA |
| (0.70, 1.00] | 75.00% | 60.00% | **UNDERPERFORMING** |

## 4. Integrity Standards
- **Sample Minimum**: Buckets with < 5 observations are marked as `INSUFFICIENT_SAMPLE`.
- **Frozen Status**: No recalibration occurs during Phase 6 observation.
