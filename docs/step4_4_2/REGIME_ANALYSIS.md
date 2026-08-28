# Step 4.4.2 Market Regime Analysis

Strategy v2.2 performance was audited across the following market regimes (classified using NIFTY 50 200-day EMA and 20-day Realized Volatility):

| Regime | Status | Expectancy | Note |
| :--- | :--- | :--- | :--- |
| **BULL_STABLE** | PASS | High | Optimal performance environment. |
| **BULL_VOLATILE** | PASS | Moderate | High reward but higher stop-hit frequency. |
| **BEAR_STABLE** | PASS | Moderate | Strategy maintains edge in controlled descents. |
| **BEAR_VOLATILE** | PASS | Low | Minimum edge but remains profitable. |
| **SIDEWAYS** | PASS | Moderate | Range-bound capture is effective. |

## Conclusion
The strategy is **Regime Robust**. It does not rely on a single market direction for its profitability.
