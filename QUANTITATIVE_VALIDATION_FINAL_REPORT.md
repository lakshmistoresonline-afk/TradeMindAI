# TradeMind AI: Quantitative Validation Final Report

**Date**: 2026-08-17 17:36:17 UTC
**Status**: FAIL

## 1. Executive Summary
Validated 7 symbols with a total of 126 out-of-sample signals.
Win Rate: 38.38% | Avg Profit: 0.07% | Brier Score: 0.3397

## 2. Methodology
- **Data Split**: Chronological split (Last 6 months used for OOS validation).
- **Leakage Prevention**: No future data used in feature engineering (Verified by Time-Safe Slicing).
- **Outcome Policy**: Conservative (Same-candle Target/Stop assume Stop first).

## 3. Results Matrix
| Metric | Result |
| :--- | :--- |
| Universe Coverage | PASS (199/200) |
| Leakage Test | PASS |
| Calibration | WEAK |
| Expected Value | VALIDATED |
| No-Trade Logic | VERIFIED |

