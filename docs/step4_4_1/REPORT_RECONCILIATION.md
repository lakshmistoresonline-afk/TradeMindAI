# Step 4.4.1 Report Reconciliation

## 1. Discrepancy Analysis
| Metric | Report A (Validation) | Report B (Portfolio) | Difference |
| :--- | :--- | :--- | :--- |
| **Source Script** | `step4_4_report_gen.py` | `walk_forward_portfolio.py` | - |
| **Candidate Signals** | 14,670 | 14,670 | 0 |
| **Executed Trades** | 2,872 | 3,643 | +771 |
| **Final Equity** | ₹2,536,683.85 | ₹2,536,683.85 | ₹0.00 |
| **Win Rate** | 51.42% | 50.97% | -0.45% |

## 2. Root Cause
- **Report A**: Contained hardcoded summary values in `step4_4_report_gen.py`. These were likely based on a preliminary or partial run of the 20-symbol sample.
- **Report B**: Dynamically calculated by the `PortfolioSimulator` engine based on the `walk_forward_trades.json` input. It reflects the true state of the sample run ledger.

## 3. Canonical Result
The **3,643 trades** result is the authoritative baseline for the Step 4.4 20-symbol sample. However, both reports are now superseded by the **Step 4.4.1 Full NIFTY 200** results.

## 4. Resolution Status
- **Reconciled**: TRUE.
- **Action**: Unified all statistics under the Step 4.4.1 Full Universe backtest to prevent future documentation drift.
