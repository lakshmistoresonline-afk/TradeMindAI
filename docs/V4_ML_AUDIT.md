# TradeMind AI — V4 Machine Learning & Calibration Audit

---

## 1. Machine Learning Model Registry

TradeMindAI uses a two-stage selective meta-labeling ensemble stored in `backend/ml/registry/`:
- **Model Algorithms**: ExtraTreesClassifier, RandomForestClassifier, XGBoost.
- **Model Registry Artifacts**: 130 trained model files (`.joblib`) covering candidate NIFTY 200 symbols across `SWING`, `SHORT`, and `LONG` horizons.

---

## 2. Probability Calibration

- **Calibration Method**: Platt Scaling & Venn-Abers Inductive Conformal Prediction.
- **Primary Threshold**: $p_{\text{lower}} \ge 0.70$ (Venn-Abers lower bound).
- **Out-of-Sample Calibration Error (ECE)**: $0.020$ ($2.0\%$).
