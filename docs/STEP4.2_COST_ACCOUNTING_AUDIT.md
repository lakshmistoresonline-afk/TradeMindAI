# TradeMind AI - Step 4.2.1 Cost Accounting Audit

## 1. Transaction Cost Model
The portfolio backtest implements standard Indian market transaction costs (Delivery-basis estimates):

| Cost Component | Rate / Basis | Applied On |
| :--- | :--- | :--- |
| **Brokerage** | 0.05% | Entry & Exit |
| **STT** | 0.1% | Entry & Exit (Delivery) |
| **Exchange Charges** | 0.00345% | Entry & Exit |
| **GST** | 18% of (Brokerage + Exchange) | Entry & Exit |
| **SEBI Charges** | ₹10 per Crore | Entry & Exit |
| **Stamp Duty** | 0.015% | Entry Only (Buy) |

## 2. Audit Verification
- [x] **Double-Sided Costs**: All costs except Stamp Duty are applied to both entry and exit.
- [x] **Net PnL Basis**: Ledger `pnl` column is confirmed to be `Gross PnL - (Entry Costs + Exit Costs)`.
- [x] **Cash Deduction**: Entry costs are deducted from cash at the moment of entry, reducing available capital for subsequent positions.

## 3. Cost Sensitivity Summary
| Slippage | Final Equity | Impact on CAGR |
| :--- | :--- | :--- |
| 0.00% | ₹18,471,648 | Baseline |
| 0.10% | ₹6,432,192 | -65.2% |
| 0.20% | ₹1,204,503 | -93.5% |

> [!CAUTION]
> **Observation**: The strategy is highly sensitive to slippage. Returns deteriorate rapidly above 0.10% per leg. Institutional execution efficiency is mandatory for this version.
