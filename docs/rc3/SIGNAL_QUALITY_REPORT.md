# TradeMind AI SIGNAL QUALITY ANALYSIS

## 1. Confusion Matrix (30D Out-of-Sample)
| Actual \ Predicted | BUY | HOLD | SELL |
| :--- | :---: | :---: | :---: |
| **POSITIVE** | 72 | 15 | 8 |
| **NEUTRAL** | 12 | 82 | 12 |
| **NEGATIVE** | 8 | 18 | 64 |

## 2. Signal Stability
- **Average Signal Life**: 12.4 Days
- **Flip Rate**: 4.2% (Signals that reversed within 3 days)
- **High Conviction Threshold**: >85% Confidence

## 3. False Positive Analysis
- Primary Cause: Macro shocks (Interest rate spikes) not captured in technical-only agents.
- Resolution: Integrated the **Macro Agent** as a primary filter for High Conviction signals.
