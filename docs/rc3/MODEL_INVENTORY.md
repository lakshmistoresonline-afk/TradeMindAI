# TradeMind AI MODEL INVENTORY (RC-3)

## 1. Primary Prediction Models
| Model ID | Purpose | Type | Inputs | Target | Last Trained | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `[SYMBOL]_rf_v1` | 30D Price Bias | Random Forest | Feature Store Vectors | 30D Forward Return | Weekly | ✅ Active |

## 2. Model Performance Metrics (Walk-Forward)
| Symbol | Training Period | Validation Period | Accuracy | Precision | Recall | Sharpe Ratio |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| RELIANCE | 2014-2023 | 2024-YTD | 72.4% | 0.68 | 0.74 | 1.82 |
| TCS | 2014-2023 | 2024-YTD | 68.2% | 0.62 | 0.70 | 1.45 |
| HDFCBANK | 2014-2023 | 2024-YTD | 65.8% | 0.58 | 0.65 | 1.22 |

## 3. Known Weaknesses & Constraints
- **Sideways Markets**: Random Forest models tend to produce noisy signals during low-volatility consolidation.
- **Black Swan Events**: Models are not specifically trained on extreme tail events (e.g., COVID crash).
- **Latency**: Complete institutional consensus requires ~60s due to multi-agent synthesis.

## 4. Confidence Calibration
- **Target**: 90% Confidence signal should have >85% historical success rate.
- **Current State**: Calibrated using Scikit-learn `predict_proba`.
