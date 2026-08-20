# TradeMind AI - Step 4.1.1 Statistics Integrity Report

## Audit Assertions
- [x] `total_trades == wins + losses + expired`
- [x] `unresolved == 0`
- [x] Every result outcome in `{TARGET_HIT, STOP_LOSS, EXPIRED}`
- [x] `profit_pct` verified for EXPIRED trade (BPCL: -0.4303%)

## Final Corrected Statistics

| Metric | Value | Basis |
| :--- | :--- | :--- |
| **Total Trades** | 37,876 | Wins + Losses + Expired |
| **Wins** | 18,637 | TARGET_HIT |
| **Losses** | 19,238 | STOP_LOSS |
| **Expired** | 1 | Evaluated but timed out (Realized) |
| **Unresolved** | 0 | All trades have realized outcome |
| **Win Rate** | 49.21% | Wins / (Wins + Losses) |
| **Avg Return** | 0.3857% | Including Expired profit/loss |
| **Total Return** | 14607.34% | Including Expired profit/loss |
| **Max Drawdown** | -94.60% | Derived from cumulative returns |

## Case Study: EXPIRED Trade
- **Symbol**: BPCL
- **Date**: 2024-03-20
- **Actual Entry**: 278.85
- **Exit Price**: 277.65
- **Realized PnL**: -0.4303%
- **Status**: Included in aggregate statistics as a realized loss.

## Final Status
**STATUS**: `STEP4.1_STATISTICS_INTEGRITY_VERIFIED`
