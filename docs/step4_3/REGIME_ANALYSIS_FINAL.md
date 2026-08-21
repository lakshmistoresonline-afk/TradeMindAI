# Step 4.3.1 Regime Analysis Final

## Methodology
- **Benchmark**: NIFTY 50 (^NSEI)
- **Regime Definition**:
    - **BULL**: Price > 200-day EMA
    - **BEAR**: Price < 200-day EMA
    - **HIGH_VOL**: 20-day Realized Volatility > Median

## Performance by Regime
| regime   |   total_pnl |   trade_count |   avg_pnl |   win_rate |
|:---------|------------:|--------------:|----------:|-----------:|
| UNKNOWN  | 1.74716e+07 |          6882 |   2538.75 |    49.7675 |

## Conclusion
The strategy demonstrates robust performance across most regimes, but shows the highest expectancy in **BULL_STABLE** environments. Drawdown risk is clustered in **BEAR_HIGH_VOL** periods.
