# TradeMind AI - Step 4.2 Portfolio Backtest Architecture Audit

## 1. Input Source
- **File**: `docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json`
- **Format**: JSON containing 37,876 trade records.
- **Verification Status**: STEP4_EXECUTION_SEMANTICS_VERIFIED, STEP4.1_STATISTICS_INTEGRITY_VERIFIED.
- **Checksum**: Will be calculated during runtime to ensure immutability.

## 2. Portfolio Engine Architecture
- **Layer**: NEW independent layer on top of Step 4.1.
- **Logic**: Event-based chronological processing of signals.
- **Components**:
    - **Event Scheduler**: Orders signals by `signal_date`, `probability`, and `symbol`.
    - **Position Manager**: Tracks active positions, concurrent counts, and symbol exposure.
    - **Risk Engine**: Implements Fixed Fractional position sizing (e.g., 1% risk per trade).
    - **Accounting Layer**: Separates Long and Short P&L, applies slippage/costs.
    - **Report Generator**: Produces equity curves, sensitivity matrices, and annual/monthly performance.

## 3. Position Overlap & Execution
- **Signal Overlap**: Multiple signals can occur on the same day across different symbols.
- **Same-Symbol Policy**: Multiple concurrent signals for the same symbol are REJECTED by default.
- **Opposite-Signal Policy**: LONG and SHORT on the same symbol do not auto-reverse; second signal is REJECTED.
- **Deterministic Entry**: If multiple signals occur on the same day, priority is:
    1. Timestamp (if available)
    2. Higher Calibrated Probability
    3. Symbol (Alphabetical)

## 4. Execution Costs & Slippage
- **Slippage**: Configurable % applied to entry and exit prices (increases entry, decreases exit for LONG).
- **Transaction Costs**: Modular cost layer for Brokerage, STT, Exchange Charges, GST, Stamp Duty.
- **Basis**: P&L is calculated based on `actual_entry` from Step 4.1.

## 5. Local Execution Model
- **Environment**: Manual local execution via PowerShell script.
- **Cloud Restriction**: NO Railway workers or background jobs.
- **Persistence**: Results saved to `data/results/` and `docs/`.

## 6. Identified Risks
- **Survivorship Bias**: Signals only represent surviving NIFTY 200 constituents. Mark as `SURVIVORSHIP_BIAS_RISK`.
- **Benchmark**: Comparison pending availability of historical index data.
- **Liquidity**: Finite capital simulation will expose if 10M liquidity gate is sufficient for large portfolios.
