# TradeMindAI — Phase E Model Performance Report

**Service Component**: [backend/services/ml_service.py](file:///D:/TradeMindAI/backend/services/ml_service.py)

---

## 1. Machine Learning Predictive Performance Metrics

Out-of-sample (OOS) evaluation metrics recorded during `MLService.train_and_register()`:
- **Accuracy**: Fraction of correct directional predictions ($> 0.50$ baseline).
- **Precision**: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$.
- **Recall**: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$.
- **F1 Score**: Harmonic mean of Precision and Recall.
- **ROC AUC**: Area Under ROC Curve (requires $> 0.55$ for SWING, $> 0.65$ for LONG).
- **Brier Score (Calibrated)**: Mean squared error of calibrated probability estimates ($\le 0.25$).
- **Expected Calibration Error (ECE)**: Measures calibration accuracy across probability bins.

---

## 2. Model & Strategy Metric Separation

TradeMindAI strictly distinguishes ML model predictive metrics (ROC AUC, Accuracy, Brier Score) from Strategy outcome performance (Win Rate, Profit Factor, Net Return, Max Drawdown). High ML Accuracy alone does NOT qualify a signal for publication if Risk Geometry or Quality Gates fail.
