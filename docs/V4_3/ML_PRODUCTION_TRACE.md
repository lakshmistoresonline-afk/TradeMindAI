# TradeMind AI — ML Production Model Trace (Step 53)

---

## 1. ML Model Artifacts & Production Inference Trace

| Model Family | Artifact Count | Loaded in Production | Inference Function | Features Verified | Calibration Verified | Production Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ExtraTrees** | 45 `.joblib` files | Yes | `predict_proba()` | 8 Feature Families | Venn-Abers Lower Bound ($p_L \ge 0.70$) | Direction & Score |
| **RandomForest** | 45 `.joblib` files | Yes | `predict_proba()` | 8 Feature Families | Platt Scaling / Isotonic | Direction & Score |
| **XGBoost** | 40 `.joblib` files | Yes | `predict_proba()` | 8 Feature Families | Conformal Bounds | Direction & Score |

---

## 2. Model Registry Location
- **Path**: `G:\TradeMindAI\backend\ml\registry\`
- **Total Trained Artifacts**: 130 `.joblib` files
- **Inference Caller**: `backend/services/signal_quality_gate.py`
