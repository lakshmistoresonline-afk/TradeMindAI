# TradeMind AI: Probability Calibration Report (Quant Validation 1.0)

## Overview
This report evaluates the accuracy and calibration of the model-predicted probabilities against realized outcomes for Strategy V2.2.

## 1. Accuracy Metrics
| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **Brier Score** | **0.2467** | Lower is better. Typical for calibrated financial models (target < 0.25). |
| **Log Loss** | **0.6893** | Measures uncertainty. Near the baseline of 0.693 for random guessing, but slightly better. |
| **ROC-AUC** | **0.5595** | Discriminatory power. 0.5 is random; 0.56 shows a slight but measurable edge in ranking. |

## 2. Calibration Analysis
- **Predicted vs. Actual**: The model consistently predicts probabilities in the 55-75% range.
- **Reliability Curve**:
    - Predicted: ~75% (recon signals) -> Actual Win Rate: 20/30 (66.6%)
    - Predicted: ~58% (sig signals) -> Actual Win Rate: 9/19 (47.3%)
- **Systematic Bias**: The model appears to slightly over-estimate confidence in some segments (75% predicted vs 66.6% actual).

## 3. Forensic Edge Validation
- **EV Correlation**:
    - Correlation between Predicted EV and Realized Net P&L: **Positive** (Heuristic based on Win Rate vs Prob).
    - **Edge Cases**: Signal `sig_BLUEDART_SHORT_202609150524` shows 99.9% probability, which may indicate extreme confidence or a calibration outlier.

## 4. Recommendations
- **Recalibration**: Implement Platt scaling or Isotonic regression for the next model iteration (V2.3) to tighten the Brier score.
- **Data Completeness**: Ensure `raw_probability` is always persisted alongside `calibrated_probability` for forensic drift detection.

---
**Audit Date**: 2026-09-16
**Status**: VALIDATED (Weak Edge)
