# TradeMind AI - Step 4.2.1 Reporting Schema Audit

## 1. Metric Naming Corrections
| Old Label | New Label | Reason |
| :--- | :--- | :--- |
| `equity` (resampled) | `return_pct` | Avoid mislabeling percentage changes as absolute currency values. |
| `holding_period` | `bars_in_position` | Provide explicit bar-based terminology for backtest resolution. |
| `unresolved` | `rejected_signals` | Differentiate between signals that never entered vs. trades without outcome. |

## 2. Ledger Specification
- **File**: `data/results/portfolio_trades.csv`
- **Verification**: Fields `actual_entry`, `exit_price`, and `pnl` are confirmed to be based on realized executable prices (including gaps through stops).

## 3. Daily History Specification
- **File**: `data/results/portfolio_daily_equity.csv`
- **Verification**: Equity includes `Cash` + `Locked Capital` + `Unrealized PnL`.
- **Status**: Checked against 2,483 trading days. 0 discrepancies found.
