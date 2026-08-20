# TradeMind AI - Step 4 True Corrected Baseline Report

## GROSS BACKTEST SUMMARY

| Metric | Value |
| :--- | :--- |
| **Total Trades** | 38,097 |
| **Wins (TARGET_HIT)** | 17,944 |
| **Losses (STOP_LOSS)** | 20,153 |
| **Expired** | 0 |
| **Win Rate** | 47.10% |
| **Average Return** | 0.1863% |
| **Total Return** | 7097.79% |
| **Profit Factor** | 1.1315 |
| **Expectancy** | 0.1863% |
| **Max Drawdown** | -96.80% |

## Execution Breakdown

| Metric | LONG | SHORT |
| :--- | :--- | :--- |
| **Count** | 27,912 | 10,185 |
| **Win Rate** | 49.24% | 41.24% |

## Gap Analysis

| Entry Type | Count | Win Rate | Loss Rate |
| :--- | :--- | :--- | :--- |
| **Normal (Intrabar)** | 23,520 | 53.27% | 46.73% |
| **Favorable Gap (Open)** | 14,577 | 37.15% | 62.85% |

## Holding Period Analysis

| Metric | Value (Bars) |
| :--- | :--- |
| **Average Holding Period** | 3.47 |
| **Median Holding Period** | 2.00 |

## Slippage & Transaction Costs Diagnostic

| Slippage Assumption | Net Avg Return | Net Total Return | Institutional Viability |
| :--- | :--- | :--- | :--- |
| **0.00% (Gross)** | 0.1863% | 7097.79% | HIGH (Theoretical) |
| **0.10% / trade** | 0.0863% | 3288.09% | MARGINAL |
| **0.20% / trade** | -0.0137% | -521.61% | UNPROFITABLE |
| **0.30% / trade** | -0.1137% | -4331.31% | UNPROFITABLE |
| **0.50% / trade** | -0.3137% | -11950.71% | FATAL |

## Portfolio Validation
**STATUS**: `PORTFOLIO_VALIDATION_PENDING`

The current results assume unlimited capital for overlapping positions. A true portfolio simulation is required to determine the realized equity curve.

## Final Status
**STATUS**: `STEP4_BASELINE_VERIFIED`

### Verification Checklist
1. `[x]` OutcomeEngine patched (Limit gap semantics)
2. `[x]` 322 forensic cases pass (All converted to STOP_LOSS at executable prices)
3. `[x]` Full 38,097 backtest passes (Removed invalid gap-against entries)
4. `[x]` No unresolved trades caused by engine state errors
5. `[x]` Entry/Exit chronology passes (signal <= entry <= exit)
6. `[x]` Stop enforcement passes (Gaps through stops captured)
7. `[x]` Favorable gap execution passes
8. `[x]` Holding-period fields pass (bars_in_position used)
9. `[x]` Drawdown independently verified (-96.8%)
