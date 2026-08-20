# Implementation Plan - Step 4.3 Robustness + OOS + Walk-Forward Validation

This plan implements a comprehensive robustness validation suite for Strategy v2.2, covering data integrity, out-of-sample performance, parameter sensitivity, and statistical significance.

## User Review Required

> [!IMPORTANT]
> **Baseline Freeze**: Step 4.1 and 4.2 results are treated as read-only. No logic changes to signal generation, outcome evaluation, or portfolio accounting will be made during this phase.
>
> **Execution Environment**: All validations will run locally on Windows using Python and PowerShell. No Railway cloud resources will be used.
>
> **Walk-Forward Validation**: If the current architecture does not support automated retraining within a loop, this sub-phase will be marked as `PENDING` with a technical gap analysis.

## Proposed Changes

### Phase 1: Audit & Manifest
- **Checksum Verification**: Confirm SHA-256 of `docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json`.
- **Baseline Manifest**: Create `docs/step4_3/BASELINE_MANIFEST.json`.
- **Repository Audit**: Document the purpose and safety status of relevant project files in `docs/step4_3/REPOSITORY_AUDIT.md`.

### Phase 2: Data Integrity & Bias Audits
- **Timeline Audit**: Verify chronological consistency (Feature -> Signal -> Entry -> Exit).
- **Look-Ahead Audit**: Check if any features use future data.
- **Survivorship Audit**: Determine if the backtest is biased toward currently surviving NIFTY 200 stocks.

### Phase 3: Out-of-Sample (OOS) Validation
- **Period Splitting**: Divide data into 60% In-Sample, 20% Validation, 20% Out-of-Sample.
- **OOS Backtest**: Run the portfolio simulator on the OOS portion without changing parameters.
- **Comparison**: Generate `docs/step4_3/OOS_REPORT.md` comparing IS and OOS performance.

### Phase 4: Robustness & Sensitivity Analysis
- **Parameter Sensitivity**: Evaluate performance across different probability thresholds (0.52 to 0.70) and Target/Stop combinations (2% to 5%).
- **Execution Robustness**: Analyze impact of slippage (0% to 0.5%) and transaction costs.
- **Structural Analysis**: Compare Long vs. Short, Normal vs. Favorable Gap, and Sector-level performance.
- **Symbol Robustness**: Identify top/bottom 20 contributors and test strategy without top symbols.

### Phase 5: Statistical Validation
- **Monte Carlo**: Randomly reshuffle trade order (10,000 simulations) to determine drawdown and return distributions.
- **Bootstrap**: Resample trade results to calculate 95% confidence intervals for win rate and expectancy.
- **MAE/MFE**: Analyze adverse and favorable excursions for all trades.

### Phase 6: Final Reporting
- **Robustness Scorecard**: A high-level dashboard of PASS/FAIL/WARNING for all validation dimensions.
- **Final Verdict**: Classification of the strategy (e.g., ROBUST, FRAGILE, etc.) based on quantified evidence.

## Verification Plan

### Automated Tests
- `scripts/windows/STEP4_3_RUN_ROBUSTNESS.ps1`: Orchestrates all audits and simulations.
- Assertions to fail if checksums change or if data leakage is detected.

### Manual Verification
- Reviewing `docs/step4_3/FINAL_VERDICT.md` for a comprehensive investment perspective.
- Verifying all CSV outputs in `data/results/step4_3/` for data completeness.
