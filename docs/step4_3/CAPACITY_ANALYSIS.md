# TradeMind AI - Step 4.3 Capacity Analysis

## Capital Sensitivity Matrix
|   capital |     final_equity |   return | status   |
|----------:|-----------------:|---------:|:---------|
|     50000 | 911844           |  1723.69 | PASS     |
|    100000 |      1.84011e+06 |  1740.11 | PASS     |
|    500000 |      9.23335e+06 |  1746.67 | PASS     |
|   1000000 |      1.84716e+07 |  1747.16 | PASS     |
|   2500000 |      4.61759e+07 |  1747.04 | PASS     |
|   5000000 |      9.23727e+07 |  1747.45 | PASS     |
|  10000000 |      1.84757e+08 |  1747.57 | PASS     |

## Liquidity Audit
- **Average Position Value**: 100,000.00 (at 1M capital)
- **Max Liquidity Gate**: 10M Average Daily Volume
- **Capacity Constraint**: The strategy is highly scalable up to 1 Crore. Beyond this, market impact analysis on the 10M volume filter is required.

## Conclusion
Strategy performance is stable across capital ranges from 50,000 to 1 Crore. Smaller portfolios (< 100k) suffer slightly more from transaction costs due to minimum brokerage assumptions.
