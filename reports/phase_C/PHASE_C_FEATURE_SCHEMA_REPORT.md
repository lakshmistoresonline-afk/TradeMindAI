# TradeMindAI — Phase C Feature Schema Integrity Report

**Service Component**: [backend/services/ml_service.py](file:///D:/TradeMindAI/backend/services/ml_service.py)

---

## 1. Feature Schema Validation & Rejection Rules

In `MLService.predict_with_champion()`:
1. **Required Feature Schema Check**:
   - Inspects `champion.hyperparameters["feature_names"]`.
   - Identifies any missing feature keys: `missing_cols = [f for f in feature_names if f not in feature_vector]`.
   - If missing features exist, inference fails closed with:
     ```json
     {
       "prediction": "UNAVAILABLE",
       "confidence": 0.0,
       "metadata": {
         "status": "SCHEMA_VALIDATION_FAILURE",
         "reason": "Missing required model features: ['f3']"
       }
     }
     ```
2. **Numeric Finiteness Guard**:
   - Validates that all values in `X_input` are finite numbers (`np.isfinite()`).
   - If `NaN` or `Infinity` (`np.inf`, `-np.inf`) values exist, inference fails closed with:
     ```json
     {
       "prediction": "UNAVAILABLE",
       "confidence": 0.0,
       "metadata": {
         "status": "NON_FINITE_FEATURES",
         "reason": "Feature vector contains NaN or Infinity values"
       }
     }
     ```
3. **No Silent Zeroing**:
   - Replaced previous `X_input.fillna(0)` behavior with explicit schema rejection.

---

## 2. Test Verification Evidence

- `test_phase_c_missing_required_features_schema_rejection`: **PASSED**
- `test_phase_c_non_finite_features_rejection`: **PASSED**
