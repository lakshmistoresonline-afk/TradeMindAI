# TradeMindAI — Phase E Transaction Cost & Slippage Report

**Audit Area**: Transaction Costs, Statutory Taxes, Brokerage, and Slippage Deductions

---

## 1. Institutional Cost & Slippage Model

To ensure research backtest returns reflect realistic net profitability rather than gross theoretical gains, TradeMindAI applies a conservative roundtrip friction model:
- **Statutory Taxes & Brokerage Fees**: $0.10\%$ entry + $0.10\%$ exit = **$0.20\%$ roundtrip** (covers STT, exchange turnover fees, SEBI charges, GST, and brokerage).
- **Execution Slippage Model**: $0.05\%$ entry + $0.05\%$ exit = **$0.10\%$ roundtrip** (5 bps per trade side).
- **Total Roundtrip Friction**: **$0.30\%$ of trade notional value**.

### Net Return Formula
$$\text{Effective Entry} = \text{Entry} \times (1 + \text{Slippage} + \text{Fees}) = \text{Entry} \times 1.0015$$
$$\text{Effective Exit} = \text{Exit} \times (1 - \text{Slippage} - \text{Fees}) = \text{Exit} \times 0.9985$$
$$\text{Net Return \%} = \frac{\text{Effective Exit} - \text{Effective Entry}}{\text{Effective Entry}} \times 100\%$$

---

## 2. Test Verification Evidence

`test_phase_e_transaction_cost_and_slippage_deduction` in `backend/tests/unit/test_phase_e_historical_backtesting.py`:
- For a trade with gross gain of $+10.0\%$ (Entry $1000.0$, Exit $1100.0$):
  - Gross Return = **$+10.00\%$**
  - Net Return = **$+9.67\%$** (after deducting $0.30\%$ total friction).
