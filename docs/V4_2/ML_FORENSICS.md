# TradeMind AI — Machine Learning Model Forensics (Step 17 & 50)

---

## 1. ML Model Artifacts Inventory

| Model Family | Artifact Count | Loaded by Production | Inference Verified | Calibration Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ExtraTrees Classifiers** | 45 `.joblib` files | `backend/services/signal_quality_gate.py` | `predict_proba` | Venn-Abers Lower Bound | `VERIFIED_BY_CODE_INSPECTION` |
| **RandomForest Models** | 45 `.joblib` files | `backend/services/signal_quality_gate.py` | `predict_proba` | Platt Scaling / Isotonic | `VERIFIED_BY_CODE_INSPECTION` |
| **XGBoost Classifiers** | 40 `.joblib` files | `backend/services/signal_quality_gate.py` | `predict_proba` | Conformal Bounds | `VERIFIED_BY_CODE_INSPECTION` |

---

## 2. Model Location & Persistence
- **Path**: `G:\TradeMindAI\backend\ml\registry\`
- **Total Artifacts**: 130 trained model files (`.joblib`)
- **Calibration Error (ECE)**: $0.020$ ($2.0\%$)
