# Step 4.2 Trade Count Reconciliation

## 1. Discrepancy Observed
- **Baseline Manifest**: 37,876 trades / 49.21% Win Rate.
- **Previous Reports**: 6,882 trades / 49.77% Win Rate.
- **Constant**: Final Equity ₹18,471,648.51.

## 2. Definitive Reconciliation
The discrepancy is caused by measuring different stages of the Strategy v2.2 execution funnel:

| Term | Definition | Source File | Count |
| :--- | :--- | :--- | :--- |
| **SIGNALS** | Raw output of SignalEngine reaching >0.52 threshold. | `STEP4_FULL_REALIZED_BACKTEST_RESULTS.json` | 37,876 |
| **CANDIDATE TRADES** | Signals processed by OutcomeEngine for realized ROI. | `STEP4_FULL_REALIZED_BACKTEST_RESULTS.json` | 37,876 |
| **EXECUTED TRADES** | Signals that passed Portfolio constraints (Capital, Max Positions). | `data/results/portfolio_trades.csv` | 6,882 |
| **FILLS** | Individual execution records (equal to Executed Trades). | `data/results/portfolio_trades.csv` | 6,882 |

## 3. Conclusion
- The **6,882** figure is the canonical **Executed Trade Count** for the ₹1M portfolio simulation.
- The **37,876** figure is the **Signal Universe Count**, representing the model's total edge across the entire dataset without capital constraints.
- **Status**: VERIFIED & EXPLAINED.
