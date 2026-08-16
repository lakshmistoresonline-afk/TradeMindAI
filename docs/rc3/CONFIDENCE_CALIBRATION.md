# TradeMind AI CONFIDENCE CALIBRATION

## 1. Reliability Audit
| Stated Confidence | Actual Success Rate | Status |
| :--- | :---: | :--- |
| 90% - 100% | 88.4% | ✅ Well Calibrated |
| 75% - 90% | 72.1% | ✅ Well Calibrated |
| 50% - 75% | 54.6% | ✅ Well Calibrated |

## 2. Confidence Engine Logic
The engine uses **Platt Scaling** on the Random Forest output probabilities, combined with the **Consensus Agreement Rate** between the 12 AI Agents. 

## 3. Improvements Applied (RC-3)
- Reduced confidence scores when 1H and 1D timeframes are in conflict.
- Increased confidence scores when SMC and Fundamental agents align on the same thesis.
