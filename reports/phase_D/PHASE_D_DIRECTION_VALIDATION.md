# TradeMindAI — Phase D Direction Validation Report

**Gate Service**: [backend/services/signal_validator_service.py](file:///D:/TradeMindAI/backend/services/signal_validator_service.py)

---

## 1. Allowed Direction Matrix

`SignalValidatorService.validate_publication()` enforces strict direction classification:
- **`LONG` / `BUY`**: Valid upward directional signal $\implies$ Accepted.
- **`SHORT` / `SELL`**: Valid downward directional signal $\implies$ Accepted.
- **`NEUTRAL`**: Flat / non-directional prediction $\implies$ Rejected (`NON_DIRECTIONAL_PREDICTION`).
- **`UNAVAILABLE`**: Missing champion model or corrupted inference $\implies$ Rejected (`NON_DIRECTIONAL_PREDICTION`).
- **Null / Empty / Unknown**: Missing or malformed direction $\implies$ Rejected (`NON_DIRECTIONAL_PREDICTION`).

---

## 2. Protected File Line 125 Read-Only Audit

- **Location**: [backend/services/signal_engine.py#L125](file:///D:/TradeMindAI/backend/services/signal_engine.py#L125)
- **Source Code**:
  ```python
  direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
  ```
- **Audit Findings**:
  - `signal_engine.py` is protected under Phase safety instructions and must remain read-only.
  - Line 125 maps `prediction == "UP"` to `LONG`, and all other labels (`DOWN`, `NEUTRAL`, `UNAVAILABLE`) to `SHORT`.
  - **Fail-Closed Gate Protection**: In `EquitySignalGenerationService` and `SignalLedgerService`, TradeMindAI enforces BUY-only publication eligibility (`is_eligible_buy(signal)`). All `SHORT` signals are immediately rejected and blocked from publication.

---

## 3. Test Execution Evidence

- `test_phase_d_valid_long_signal_passes_validation`: **PASSED**
- `test_phase_d_valid_short_signal_passes_validation`: **PASSED**
- `test_phase_d_neutral_or_unavailable_direction_rejected`: **PASSED**
