# TradeMindAI — Phase C Prediction Direction Mapping Report

**Component**: [backend/services/ml_service.py](file:///D:/TradeMindAI/backend/services/ml_service.py) & [backend/services/signal_engine.py](file:///D:/TradeMindAI/backend/services/signal_engine.py)

---

## 1. Prediction Label Contract

Function `MLService.predict_with_champion()` maps calibrated probability $P(\text{UP})$ into 4 distinct directional prediction labels:
1. **`UP`**: $P(\text{UP}) > 0.55 \implies$ Upward directional prediction.
2. **`DOWN`**: $P(\text{UP}) < 0.45 \implies$ Downward directional prediction.
3. **`NEUTRAL`**: $0.45 \le P(\text{UP}) \le 0.55 \implies$ Flat / non-directional prediction.
4. **`UNAVAILABLE`**: Missing champion model, corrupted model file, missing required features, non-finite inputs, or inference error.

---

## 2. Protected File Line 125 Mapping Audit

- **Location**: [backend/services/signal_engine.py#L125](file:///D:/TradeMindAI/backend/services/signal_engine.py#L125)
- **Source Code**:
  ```python
  direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
  ```
- **Audit Evaluation**:
  - `signal_engine.py` is protected under Phase safety instructions and must remain read-only.
  - Line 125 maps `prediction == "UP"` to `LONG`, and all other labels (`DOWN`, `NEUTRAL`, `UNAVAILABLE`) to `SHORT`.
  - **Fail-Closed Protection**: In `EquitySignalGenerationService` and `SignalLedgerService`, TradeMindAI enforces BUY-only publication eligibility (`is_eligible_buy(signal)`). All `SHORT` signals are immediately rejected and blocked from publication.
  - **Proposed Patch (Blocked Pending Authorization)**:
    ```python
    pred_label = ml_res.get("prediction")
    if pred_label == "UP":
        direction = "LONG"
    elif pred_label == "DOWN":
        direction = "SHORT"
    else:
        return None  # Fail closed on NEUTRAL, UNAVAILABLE, or missing predictions
    ```

---

## 3. Test Verification Summary

- `test_phase_c_missing_champion_model_returns_unavailable`: **PASSED**
- `test_phase_c_missing_model_file_returns_unavailable`: **PASSED**
- `test_phase_c_corrupted_model_file_fails_closed`: **PASSED**
