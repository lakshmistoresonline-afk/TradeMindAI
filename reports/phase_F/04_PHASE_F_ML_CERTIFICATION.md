# TradeMindAI — Phase F ML Certification Report

**Audited Component**: [backend/services/ml_service.py](file:///D:/TradeMindAI/backend/services/ml_service.py) & [backend/services/signal_quality_service.py](file:///D:/TradeMindAI/backend/services/signal_quality_service.py)

---

## 1. ML Inference & Schema Audit Results

1. **Model Artifact Readability**:
   - `MLService.predict_with_champion()` catches corrupted joblib load exceptions safely (`MODEL_LOAD_FAILURE`).
2. **Strict Feature Schema Validation**:
   - Compares input feature vector keys against `champion.hyperparameters["feature_names"]`.
   - Rejects inference if required features are missing (`SCHEMA_VALIDATION_FAILURE`).
3. **Non-Finite Value Guard**:
   - Rejects inference if input features contain `NaN` or `Infinity` (`NON_FINITE_FEATURES`).
4. **Probability Domain Validation**:
   - Validates that raw and calibrated probabilities are finite numbers in $[0.0, 1.0]$.
5. **Directional Mapping Contract**:
   - Calibrated probability $> 0.55 \implies$ `UP`.
   - Calibrated probability $< 0.45 \implies$ `DOWN`.
   - $0.45 \le P \le 0.55 \implies$ `NEUTRAL`.
   - Missing champion / corrupted model / schema error $\implies$ `UNAVAILABLE`.
6. **Publication Gates**:
   - `SignalQualityService.should_publish()` fails closed if model is unregistered (`model is None`), test sample size $< 20$, ROC AUC $\le 0.52$, or probability $< 0.52$.

---

## 2. Test Execution Evidence

- `test_phase_c_missing_champion_model_returns_unavailable`: **PASSED**
- `test_phase_c_missing_model_file_returns_unavailable`: **PASSED**
- `test_phase_c_corrupted_model_file_fails_closed`: **PASSED**
- `test_phase_c_missing_required_features_schema_rejection`: **PASSED**
- `test_phase_c_non_finite_features_rejection`: **PASSED**
- `test_phase_c_signal_quality_service_fails_closed_on_unregistered_or_weak_model`: **PASSED**
