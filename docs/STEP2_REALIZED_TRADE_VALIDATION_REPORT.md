# Step 2: Realized Signal & Trade Outcome Validation Report

**Audit Timestamp**: 2026-08-17 07:15:00 UTC
**Status**: FAIL - OUTCOME PIPELINE DEFECT

## 1. Executive Summary
The forensic audit of realized trade outcomes has identified a **critical logic defect** in the `SignalEngine` that invalidates current performance claims. While the model's directional accuracy is ~57%, the translation into realized trades is currently failing due to incorrect probability handling for SHORT positions.

## 2. Realized Performance Metrics

| Metric | Measured (Broken) | Hypothetical (Aligned) | Status |
| :--- | :--- | :--- | :--- |
| **Trade Win Rate** | 0.00% | 35.49% | **FAIL** |
| **Realized Expectancy** | -0.50R | +0.23R | **FAIL** |
| **Theoretical Expectancy** | +0.71R | +0.71R | **PASS** |
| **Total Trades (Sample)** | 4 | 2,150 | **FAIL** |

> [!CAUTION]
> **Defect Found**: The `SignalEngine` and `CalibrationService` use `calibrated_probability_up` even for `SHORT` signals. This causes almost all `SHORT` signals to be rejected for "Negative Expectancy" or "Weak Edge," and those that pass have inverted confidence logic.

## 3. Performance Degradation Trace
I traced the performance across the quantitative pipeline:

1. **MODEL** (Directional): 57.11% Win Rate.
2. **SIGNAL FILTER**: 99.8% of SHORT signals rejected due to signed EV calculation.
3. **ENTRY**: Signal generated at Close(T), Entry checked at High/Low of [T+1...T+30].
4. **RISK ENGINE**: Sets 2.5:1 RR baseline. This mathematically lowers the win rate (targets are harder to hit than stops).
5. **OUTCOME ENGINE**: Realized Win Rate drops to 35.49% because of the tight stop (2.0x ATR) vs far target (5.0x ATR).

## 4. Horizon & Regime Analysis (Hypothetical Aligned)
| Horizon | Win Rate | Expectancy | Note |
| :--- | :--- | :--- | :--- |
| **SWING** | 35.49% | +0.23R | Positive edge verified if fixed. |
| **INTRADAY** | N/A | N/A | Insufficient granular data in local DB. |

## 5. Sample Count Reconciliation
- **RELIANCE (Forensic Trace)**: 325 samples.
- **RELIANCE (Quant Report)**: 321 samples.
- **Reason**: `run_quant_validation.py` excludes the last 5 days of the dataset because the 5-day forward target cannot be calculated yet (Look-ahead protection).

## 6. Identified Defects
| Defect | Location | Root Cause | Impact | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **SHORT Prob Mismatch** | `SignalEngine.py` | Uses `prob_up` for `SHORT` EV/Edge filters. | 99% of short trades rejected. | **CRITICAL** |
| **Signed EV Calc** | `CalibrationService.py` | Uses signed diffs `(price-stop)` which are negative for shorts. | Mathematically invalid EV for shorts. | **CRITICAL** |
| **RR Inconsistency** | `RiskEngine.py` | Hardcoded 2.5:1 vs 2:1 in reports. | Confusion in performance claims. | **MEDIUM** |

## Final Status
**STATUS: FAIL**

The system's realized expectancy is currently **negative (-0.50R)** due to implementation defects. The "68.76% Win Rate" claim in the prompt is unverified and likely refers to theoretical directional accuracy rather than realized signal performance.

**Step 2 is BLOCKED until the SignalEngine defects are resolved.**
