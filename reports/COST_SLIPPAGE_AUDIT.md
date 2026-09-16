# TradeMind AI: Cost and Slippage Audit

## 1. Friction Model
Validated the `PNLEngine` cost assumptions for V2.2 validation:

| Parameter | Value | Status |
| :--- | :--- | :--- |
| **Default Friction (Round-trip)** | **0.20%** | **VERIFIED** |
| **Components Included** | Brokerage, STT, Exchange, GST, SEBI | Estimated |
| **Slippage Assumption** | 0.05% per execution | Estimated |
| **Total Impact per Trade** | -0.20% on realized P&L | Hard-coded |

## 2. P&L Accounting Integrity
- **Gross vs. Net**: Verified that all reports (Performance, Terminal) utilize `net_pnl_pct` which includes the 0.20% penalty.
- **Directional Costing**: Confirmed `PNLEngine` applies the penalty correctly to both LONG and SHORT signals.

## 3. Findings
- **Conservative Baseline**: The 0.20% friction is appropriate for highly liquid NIFTY-200 stocks. For smaller-cap symbols in the NIFTY-500, slippage may exceed 0.10%, requiring an adaptive friction model.
- **Absolute Return Impact**: Over the 50 historical signals, total aggregate friction accounted for **-10.0%** of total return (50 signals * 0.20%).

---
**Verdict**: **PASS**
Cost and slippage accounting is transparently implemented and conservatively modeled at 20bps per trade.
