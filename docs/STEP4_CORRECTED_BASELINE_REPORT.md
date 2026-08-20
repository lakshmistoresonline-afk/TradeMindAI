# TradeMind AI - Step 4 Corrected Baseline Report

## Diagnostic Scenarios

| Metric | Scenario A (Current) | Scenario B (Hard Stop) | Scenario C (CA Safe) |
| :--- | :--- | :--- | :--- |
| **Win Rate** | 53.78% | 53.78% | 53.78% |
| **Total Trades** | 38,636 | 38,636 | 38,636 |
| **TARGET_HIT** | 20,777 | 20,777 | 20,777 |
| **STOP_LOSS** | 17,537 | 17,859 | 17,859 |
| **EXPIRED** | 322 | 0 | 0 |
| **Avg Return** | 0.25% | 0.23% | 0.23% |
| **Total Return** | 9720% | 8754% | 8754% |
| **Max Drawdown** | -92.0% | -92.7% | -92.7% |

> [!NOTE]
> **Scenario B** assumes that all `EXPIRED` trades would have hit their 3% stop loss if correctly triggered and enforced. This is the most conservative and realistic baseline.

## Slippage & Transaction Costs Audit
- **Status**: **NOT IMPLEMENTED**.
- **Finding**: The "High-fidelity slippage" claim in previous reports is incorrect. All trades are currently calculated at gross prices (exactly 3% profit/loss).
- **Recommendation**: Slippage of 0.1% to 0.5% per trade should be added to Scenario B to determine true institutional viability.

## Strategy Baseline Status
**STATUS**: `STEP4_FORENSIC_REVALIDATION_REQUIRED`

The baseline cannot be marked as `VERIFIED` until the `OutcomeEngine` code is patched to correctly handle entry gaps and enforce stops globally.
