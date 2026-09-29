# TradeMind AI — ML Model Final Audit Report (Step 50)

---

## 1. Model Registry & Inference Summary

| Model Family | Artifact Count | Loaded in Production | Executed in Production | Calibration Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ExtraTrees Classifiers** | 45 `.joblib` files | Yes | Yes | Venn-Abers Lower Bound | `VERIFIED_BY_CODE_INSPECTION` |
| **RandomForest Models** | 45 `.joblib` files | Yes | Yes | Platt Scaling / Isotonic | `VERIFIED_BY_CODE_INSPECTION` |
| **XGBoost Classifiers** | 40 `.joblib` files | Yes | Yes | Conformal Bounds | `VERIFIED_BY_CODE_INSPECTION` |

---

## 2. Artifacts Location
- **Path**: `G:\TradeMindAI\backend\ml\registry\`
- **Total Trained Artifacts**: 130 `.joblib` files
- **Inference Caller**: `backend/services/signal_quality_gate.py`
