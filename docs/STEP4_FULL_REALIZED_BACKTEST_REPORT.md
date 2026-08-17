# Step 4: Full Realized Walk-Forward Backtest Report

**Generated**: 2026-08-17 13:27:43.530008 UTC

## 1. Global Baseline Metrics

| Metric | Value | Note |
| :--- | :--- | :--- |
| Total Signals Attempted | 6477 | All test-period bars |
| Signals Accepted (Signal Accuracy) | 5475 (84.53%) | Passed EV/Edge Gate |
| Completed Trades | 4855 | Outcome reached |
| **Trade Win Rate** | **34.48%** | Target Hit / Total Completed |
| Avg Win R | 2.50R | Realized payoff |
| Avg Loss R | -1.00R | Realized risk |
| **Realized Expectancy** | **0.19R** | Per trade average |
| Profit Factor | 1.32 | Gross Win / Gross Loss |
| Max Drawdown | -542.50R | Peak-to-trough equity |
| Cumulative R | 932.95R | Total baseline return |

## 2. Directional Performance

### LONG
- Trades: 112
- Win Rate: 47.32%
- Expectancy: 0.66R

### SHORT
- Trades: 4743
- Win Rate: 34.18%
- Expectancy: 0.18R

## 3. Confidence Calibration Analysis

|    |   ('bucket', '') |   ('win', 'count') |   ('win', 'mean') |   ('realized_r', 'mean') |
|---:|-----------------:|-------------------:|------------------:|-------------------------:|
|  0 |               50 |                779 |          0.268293 |               -0.0121926 |
|  1 |               55 |               1759 |          0.268903 |                0.0385471 |
|  2 |               60 |               1912 |          0.334728 |                0.285382  |
|  3 |               65 |                669 |          0.355755 |                0.357247  |
|  4 |               70 |                231 |          0.341991 |                0.322502  |
|  5 |               75 |                123 |          0.284553 |                0.142279  |
|  6 |               80 |                  2 |          0        |               -1         |

## 4. Rejection Analysis

| Reason    |   Count |
|:----------|--------:|
| WEAK_EDGE |    1002 |

## 5. Per-Symbol Baseline (Top 50 by Trades)

| Symbol     |   Trades |   Win Rate |       Avg R |
|:-----------|---------:|-----------:|------------:|
| INFY       |      312 |   0.288462 |  0.00961495 |
| TCS        |      311 |   0.360129 |  0.26045    |
| HDFCBANK   |      304 |   0.463816 |  0.623351   |
| ICICIBANK  |      302 |   0.354305 |  0.268289   |
| ADANIGREEN |      301 |   0.315615 |  0.104659   |
| SBIN       |      296 |   0.114865 | -0.767039   |
| ADANIENSOL |      295 |   0.257627 | -0.179198   |
| ADANIENT   |      288 |   0.479167 |  0.677084   |
| APOLLOHOSP |      286 |   0.153846 | -0.461538   |
| HINDUNILVR |      274 |   0.364964 |  0.27737    |
| RELIANCE   |      267 |   0.374532 |  0.310859   |
| ACC        |      265 |   0.358491 |  0.25471    |
| ITC        |      256 |   0.640625 |  1.24216    |
| BHARTIARTL |      217 |   0.341014 |  0.193549   |
| AMBUJACEM  |      214 |   0.420561 |  0.471948   |
| APOLLOTYRE |      206 |   0.300971 |  0.0534039  |
| LICI       |      189 |   0.343915 |  0.203701   |
| ABB        |      120 |   0.333333 |  0.166667   |
| ADANIPORTS |      115 |   0.347826 |  0.168262   |
| ADANIPOWER |       37 |   0.189189 | -0.337849   |