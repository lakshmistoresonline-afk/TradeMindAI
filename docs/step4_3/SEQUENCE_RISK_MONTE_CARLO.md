# Step 4.3.1 Sequence Risk & Monte Carlo

## 1. Trade Order Sequence Risk (Shuffle)
Analyzes the impact of trade ordering on drawdown, assuming identical trade outcomes.

| Percentile | Max Drawdown |
| :--- | :--- |
| **5th** | -42.34% |
| **Median** | -20.55% |
| **95th** | -11.44% |

## 2. Trade Resampling Robustness (Bootstrap)
Analyzes the stability of returns by sampling the trade distribution with replacement.

| Metric | 95% Confidence Interval |
| :--- | :--- |
| **Net Portfolio PnL** | 13,290,569.73 to 21,585,893.51 |
| **Win Rate** | 48.59% to 50.94% |
| **Profit Factor** | 1.2732 to 1.4761 |

## Conclusion
**STATUS**: PASS. The strategy's edge is statistically stable across 10,000 resampling iterations. Sequence risk remains well-contained within a -25% median drawdown limit.
