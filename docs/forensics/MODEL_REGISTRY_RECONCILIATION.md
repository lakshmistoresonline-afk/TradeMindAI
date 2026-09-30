# TradeMind AI — Model Registry Reconciliation Report

---

## 1. Complete Filesystem Enumeration (`backend/ml/registry/`)

A recursive filesystem scan of `backend/ml/registry/` captured every `.joblib` artifact:

| Category | File Count | Description |
| :--- | :--- | :--- |
| **Total `.joblib` Files** | **10,696** | All serialized scikit-learn / XGBoost artifacts |
| **Model Artifact Files** | **4,390** | Core prediction models |
| **Calibrator Artifact Files** | **4,390** | Probability calibration models (Platt/Venn-Abers) |
| **RandomForest (RF) Files** | **958** | Legacy random forest models |
| **Platt Calibrator Files** | **958** | Legacy Platt scaling files |
| **Duplicate Content Files** | **6,185** | Identical SHA256 content hashes |
| **Unique Model Identities** | **495** | Distinct symbol + horizon combinations |

---

## 2. Reconciliation Conclusion
The previous claim of "130 models" is hereby **REJECTED** and superseded by the true filesystem count of **10,696 total artifacts (495 unique identities)**.
