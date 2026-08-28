# Step 4.3.1 Sector Robustness Final

## Sector Performance Breakdown
| sector                 |         total_pnl |   trade_count |   avg_pnl |   win_rate |
|:-----------------------|------------------:|--------------:|----------:|-----------:|
| Financial Services     |       4.41283e+06 |          2786 |  1583.93  |    47.7387 |
| Unknown                |       3.60946e+06 |           542 |  6659.53  |    55.3506 |
| Industrials            |       3.23926e+06 |           704 |  4601.22  |    50.9943 |
| Basic Materials        |       2.0709e+06  |           626 |  3308.14  |    52.0767 |
| Utilities              |       1.87023e+06 |           436 |  4289.52  |    49.3119 |
| Consumer Cyclical      |       1.53901e+06 |           281 |  5476.9   |    53.0249 |
| Communication Services |  807029           |           199 |  4055.42  |    53.2663 |
| Energy                 |  624663           |           751 |   831.775 |    47.9361 |
| Real Estate            |   76398.3         |            25 |  3055.93  |    64      |
| Healthcare             |  -52251.3         |           107 |  -488.33  |    50.4673 |
| Consumer Defensive     | -280597           |           219 | -1281.27  |    47.9452 |
| Technology             | -445287           |           206 | -2161.59  |    50.9709 |

## Stress Test: Without Top Sector (Financial Services)
- **Baseline Net PnL**: 17,471,648.51
- **PnL without Financial Services**: 13,058,817.73
- **Robustness**: PASS

## Conclusion
With fixed sector mapping, the strategy demonstrates robustness across diversified industries. No single sector accounts for the entirety of the returns.
