# Step 3B: SHORT Trade Logic Refactoring Report

**Audit Timestamp**: 2026-08-17 10:45:00 UTC
**Status**: FIX VERIFIED

## 1. Executive Summary
The forensic audit in Step 2 identified that the system had **zero realized short performance** due to mathematical defects in probability mapping and Expected Value (EV) calculation. I have refactored the signal pipeline to be direction-aware, ensuring `SHORT` trades are evaluated with the correct probabilities and positive risk/reward geometry.

## 2. Identified Defects & Root Causes

| Defect | Root Cause | Impact |
| :--- | :--- | :--- |
| **Probability Inversion** | System used `P(UP)` for both `LONG` and `SHORT`. | `SHORT` trades were evaluated with the probability of the price going against them. |
| **Signed Math Errors** | EV formula used `entry - stop`, which is negative for `SHORT`. | 99.8% of `SHORT` signals were rejected for "Negative Expectancy". |
| **Hardcoded R:R** | Risk/Reward ratio was hardcoded in `RiskEngine`. | Inconsistency with performance reports claiming 2:1. |
| **Serialization Failure** | `provenance` and `events` columns were passed as objects to SQLite. | Signal saving failed with `InterfaceError`. |

## 3. Mathematical Corrections Implemented

### A. Directional Probability
Implemented `CalibrationService.get_direction_probability(prob_up, direction)`:
- **LONG**: `prob = prob_up`
- **SHORT**: `prob = 1.0 - prob_up`
- **Pass Criteria**: `P(LONG) + P(SHORT) = 1.0` verified.

### B. Normalized Risk & Reward
Refactored `SignalEngine` to use absolute price differences:
- `risk = abs(entry - stop)`
- `reward = abs(target - entry)`
- Ensures `EV` calculation is direction-neutral and mathematically valid.

### C. Expected Value (EV)
Updated `CalibrationService.calculate_expected_value`:
- Now enforces absolute `reward_amt` and `risk_amt`.
- EV now correctly reflects the edge for the chosen trade direction.

## 4. Configuration Hardening
- **Centralized R:R**: Added `DEFAULT_RISK_REWARD` to `backend/core/config.py`.
- **Value**: Set to **2.5** (Standardizing on the existing `RiskEngine` baseline).

## 5. Verification Results

### Unit Tests (`test_short_logic.py`)
- [x] LONG probability correct (0.7)
- [x] SHORT probability correct (0.3)
- [x] P(UP)+P(DOWN)=1.0
- [x] LONG risk/reward positive
- [x] SHORT risk/reward positive
- [x] EV logic reproduces manual benchmarks
- [x] Invalid geometry rejected

### Signal Generation Trace
- **Previous State**: Almost all `SHORT` signals rejected.
- **Current State**: `SHORT` signals for `HDFCBANK`, `ICICIBANK`, `RELIANCE`, `TCS`, etc., now pass the EV gate and are successfully saved to the database.

### Data Protection Regression
- Executed `test_master_sync_safety.py`.
- **Result**: **PASS**. Candle count remained at 334,734.

## 6. Conclusion
The mathematical foundation for `SHORT` trades is now correct. The system no longer systematically discriminates against downward price moves. 

**Step 3B is PASSED.**

> [!TIP]
> The quantitative logic is now "Honest." The next step should be a full realized backtest to determine the actual performance of this corrected logic across the 6-year dataset.
