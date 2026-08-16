# Probability Calibration Report (Platt Scaling)

**Generated**: 2026-08-16 10:56:59.513746 UTC

## 1. Executive Summary

This report details the implementation of **Platt Scaling** for TradeMind AI signals. Calibration is performed out-of-sample using a chronological 60/20/20 split to ensure time-safety and statistical validity.

## 2. Sample Results (Nifty 10 Subset)

| Symbol     |   Brier (Raw) |   Brier (Cal) |   Log Loss | Improvement   |
|------------|---------------|---------------|------------|---------------|
| RELIANCE   |        0.2867 |        0.2855 |     0.7649 | YES           |
| TCS        |        0.2373 |        0.282  |     0.7642 | NO            |
| HDFCBANK   |        0.2739 |        0.2893 |     0.7764 | NO            |
| INFY       |        0.341  |        0.2881 |     0.7779 | YES           |
| ICICIBANK  |        0.2866 |        0.2512 |     0.6986 | YES           |
| BHARTIARTL |        0.2643 |        0.2439 |     0.6809 | YES           |
| SBIN       |        0.2755 |        0.2523 |     0.7059 | YES           |
| LICI       |        0.284  |        0.2523 |     0.6987 | YES           |
| ITC        |        0.3257 |        0.2605 |     0.7153 | YES           |
| HINDUNILVR |        0.3171 |        0.227  |     0.6469 | YES           |

## 3. Calibration Methodology
- **Method**: Platt Scaling (Logistic Regression on sigmoid scores).
- **Data Splitting**: Chronological (No future leakage).
- **Validation**: Evaluated on the latest 20% unseen test set.
- **Primary Metric**: Brier Score (Mean Squared Error of probability forecasts).

## 4. Reliability Assessment
Calibration generally improves the Brier score by adjusting for Random Forest's tendency to push probabilities toward the center or edges. Calibrated probabilities are now used as the primary 'Confidence' metric in the Signal Engine.
