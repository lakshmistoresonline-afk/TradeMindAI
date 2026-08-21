# Step 4.3 Survivorship Bias Audit

## Universe Definition
- **Current Constituents**: 200
- **Historical Traded Symbols in DB**: 199
- **Symbols not in current NIFTY 200**: 0

## Findings
> [!WARNING]
> **SURVIVORSHIP_BIAS_RISK**: The backtest uses current NIFTY 200 constituents applied historically.
Stocks that were delisted, merged, or moved out of the NIFTY 200 before Aug 2026 are likely missing from the dataset.

## Potential Impact
The results may overstate performance by excluding companies that failed or underperformed to the point of being removed from the index.
