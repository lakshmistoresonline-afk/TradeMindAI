# V2.2 PROBABILITY CALIBRATION ANALYSIS

## 1. Global Calibration Metrics
- **Brier Score**: 0.2626 (Lower is better, 0.25 is random guessing)
- **Log Loss**: 0.7199
- **Sample Size**: 48 signals with valid prob

## 2. Calibration Table (Predicted vs Actual)
| prob_bucket   |   ('y_true', 'mean') |   ('y_true', 'count') |   ('probability', 'mean') |
|:--------------|---------------------:|----------------------:|--------------------------:|
| (0.0, 0.5]    |            nan       |                     0 |                nan        |
| (0.5, 0.6]    |              0.46875 |                    32 |                  0.572574 |
| (0.6, 0.7]    |              0.5625  |                    16 |                  0.633153 |
| (0.7, 0.8]    |            nan       |                     0 |                nan        |
| (0.8, 0.9]    |            nan       |                     0 |                nan        |
| (0.9, 1.0]    |            nan       |                     0 |                nan        |

## 3. Findings
> [!WARNING]
> Brier score > 0.25 indicates that the probability model is performing worse than random guessing in this sample.
