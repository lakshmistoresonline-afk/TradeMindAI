# TradeMind AI: Model Availability Audit

## 1. Observed Coverage (Population N=7500)
Analyzed prediction availability across the NIFTY-200 universe:

| Category | Value |
| :--- | :--- |
| **Total Predictions** | 7,500 |
| **High Density Symbols** | RELIANCE, ACC, TCS, INFY, ICICIBANK |
| **Low Density Symbols** | 180+ Symbols with < 5 predictions |
| **Observed Skew** | Top 5 symbols account for > 60% of population |

## 2. Findings
- **Sample Bias**: Historical validation is heavily concentrated on symbols with deep liquidity and long historical price series.
- **Missing Periods**: Significant gaps exist in the 2021-2024 period for several symbols due to missing features or data quality rejections.
- **Non-Uniformity**: The observed win rate (59%) should be interpreted as the performance on the high-availability subset of the NIFTY-200.

## 3. Recommended Research
- Stabilize data ingestion for the remaining 90% of the universe to enable uniform validation.
- Audit whether the model edge persists on lower-volume constituents.

---
**Verdict**: **DATA_LIMITED**
Significant symbol availability skew detected. Results are dominated by a handful of high-history tickers.
