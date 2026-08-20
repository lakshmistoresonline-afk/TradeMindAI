# Implementation Plan - STEP 4: Critical Forensic Revalidation

This plan addresses the massive anomalies identified in the Step 4 backtest results, specifically the impossible losses (up to -245%) in `EXPIRED` trades. We will audit the `OutcomeEngine` logic, verify data continuity for extreme cases, and produce a corrected baseline for Strategy v2.2.

## User Review Required

> [!CRITICAL]
> **PHANTOM LOSSES:** The forensic audit has confirmed that 320 out of 322 `EXPIRED` trades never triggered an entry (`WAITING_FOR_ENTRY`). The system incorrectly assigned them a "realized" loss based on the price 200 bars later, despite no capital ever being committed.
>
> **SLIPPAGE AUDIT:** The previous claim of "High-fidelity slippage" has been found to be **FALSE**. The backtest orchestrator used raw `OutcomeEngine` results which exclude the 0.20% institutional friction model.
>
> **DRAWDOWN ACCOUNTING:** The -102.6% drawdown is a result of a compounding error where single-trade returns exceeded -100% (specifically in failed Short signals that never triggered).

## Proposed Forensic Changes

### 1. Algorithmic Correction
#### [MODIFY] [OutcomeEngine.py](file:///G:/TradeMindAI/backend/services/outcome_engine.py)
- Ensure that if a trade expires while still in `WAITING_FOR_ENTRY`, its `profit_pct` is strictly **0.0**.
- A trade only incurs profit/loss if it transitions to `ACTIVE`.

### 2. Corporate Action Verification
- Audit symbols like `ADANIPOWER` and `ADANIENT` for the period 2021-2023.
- Verify if the extreme moves (15 -> 53) were genuine market action or unadjusted data gaps.
- Ensure the backtest uses the most accurate adjusted pricing available in the SQLite dataset.

### 3. Reporting & Performance Recalculation
#### [NEW] [docs/STEP4_EXPIRED_FORENSIC_REPORT.md](file:///G:/TradeMindAI/docs/STEP4_EXPIRED_FORENSIC_REPORT.md)
- Detail the root cause of the "Phantom Losses."
- Provide the "Triggered-Only" win rate and expectancy.
#### [NEW] [docs/STEP4_CORRECTED_BASELINE_REPORT.md](file:///G:/TradeMindAI/docs/STEP4_CORRECTED_BASELINE_REPORT.md)
- The new authoritative baseline for Strategy v2.2.

## Verification Plan

### Automated Verification
- **Scenario B Calculation:** Run a script to filter the existing `results.json` and calculate stats excluding non-triggered trades.
- **Stop Enforcement Test:** Verify that `EXPIRED` trades did not cross the 3% stop loss while in `ACTIVE` state.

### Manual Verification
- **Equity Curve Audit:** Re-plot the equity curve using the corrected triggered-only sequence.
- **Slippage Enforcement:** Manually apply the 0.20% friction to a subset of trades to verify the impact on expectancy.

## Milestone Status
| Milestone | Status |
| :--- | :--- |
| **Phantom Loss Identified** | **CONFIRMED** |
| **Short Formula Verified** | **CONFIRMED** |
| **Logic Correction** | `PENDING_APPROVAL` |
| **Baseline Re-Verification** | `BLOCKED` |

---
**Verdict:** The baseline remains **UNVERIFIED**. I am proceeding with the logic correction upon your approval.
