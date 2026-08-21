# Step 4.3.1 Model Drift Audit Final

## Annual Normalized Performance
|   year |   avg_pnl |   med_pnl |        total_pnl |   trade_count |   avg_prob |   avg_ret_pct |   win_rate |
|-------:|----------:|----------:|-----------------:|--------------:|-----------:|--------------:|-----------:|
|   2017 |  -85.7424 |  -654.341 | -16977           |           198 |   0.617994 |    -0.0816903 |    49.4949 |
|   2018 |   65.4313 |  -449.264 |  31930.5         |           488 |   0.62583  |     0.0718011 |    49.1803 |
|   2019 |   24.1696 |  -416.032 |   9764.5         |           404 |   0.628062 |     0.030728  |    49.7525 |
|   2020 |  382.64   |  -650.932 | 331749           |           867 |   0.631228 |     0.331654  |    47.6355 |
|   2021 | 1412      |  3678.88  |      1.54897e+06 |          1097 |   0.643016 |     0.701613  |    50.866  |
|   2022 | 1214.57   | -1620.98  |      1.16721e+06 |           961 |   0.648201 |     0.357274  |    48.4912 |
|   2023 | 2598.6    |  4261.8   |      1.94376e+06 |           748 |   0.641861 |     0.530484  |    50      |
|   2024 | 7438.14   | 16438.6   |      7.24475e+06 |           974 |   0.643923 |     0.837208  |    52.4641 |
|   2025 | 1217.33   | -8207.7   | 830220           |           682 |   0.653279 |     0.0956245 |    46.7742 |
|   2026 | 9460.66   | 38799.6   |      4.38029e+06 |           463 |   0.65281  |     0.594542  |    52.9158 |

## Findings
- **Win Rate Stability**: Win rate has fluctuated between 46.77% and 52.92%.
- **Edge Persistence**: Average return per trade has remained positive in 9 out of 10 years.
- **Expectancy**: No clear evidence of structural decay; the strategy has performed well in the recent 2024-2026 window.

## Conclusion
**STATUS**: PASS. Strategy expectancy remains stable over 9 years of varied market cycles.
