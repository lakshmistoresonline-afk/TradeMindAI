# TradeMind AI - Step 4.3 Out-of-Sample Report

## Dataset Segmentation
| Split | Start | End | Trades |
| :--- | :--- | :--- | :--- |
| **In-Sample (60%)** | 2017-06-02T00:00:00 | 2023-02-07T00:00:00 | 4129 |
| **Validation (20%)** | 2023-02-07T00:00:00 | 2024-09-19T00:00:00 | 1376 |
| **Out-of-Sample (20%)** | 2024-09-20T00:00:00 | 2026-08-18T00:00:00 | 1377 |

## Performance Comparison
| Metric | In-Sample | Validation | Out-of-Sample |
| :--- | :--- | :--- | :--- |
| **Win Rate** | 49.14% | 52.69% | 48.73% |
| **Avg Return** | 0.3600% | 0.8169% | 0.2718% |
| **Profit Factor** | 1.3330 | 1.8047 | 1.2121 |
| **Total Net PnL** | 3,294,760.59 | 8,589,000.44 | 5,587,887.47 |

## Degradation Analysis
- **OOS / IS Profit Factor Ratio**: 0.91
- **OOS / IS Avg Return Ratio**: 0.75

## Conclusion
PASS: Strategy maintains positive edge in OOS.
