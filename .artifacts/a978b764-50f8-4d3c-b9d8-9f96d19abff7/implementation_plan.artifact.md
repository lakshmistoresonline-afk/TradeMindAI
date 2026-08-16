# NIFTY 200 Historical Coverage Recovery & Calibration

This plan addresses the recovery of missing historical data for the NIFTY 200 universe, enforces a strict data gate before ML processing, and implements probability calibration (Platt Scaling) for high-fidelity signals.

## User Review Required

> [!IMPORTANT]
> **Symbol Transitions**: My forensic audit discovered that several NIFTY 200 stocks have undergone name changes/demergers in the August 2026 timeline. Legitimate history for `ZOMATO`, `PEL`, and `TATAMOTORS` exists under new tickers (`ETERNAL`, `PIRAMALFIN`, `TMCV`). I will implement a provider-specific mapping to recover this data without fabrication.

> [!WARNING]
> **Strict Gate**: I am updating the validator to return a **FAIL** status if any stock is missing without a documented structural reason. Step 2 (Intelligence) will be blocked until this recovery is complete.

## Open Questions
- None. I have confirmed the new tickers via brute-force provider searches.

## Proposed Changes

### 1. Data Recovery & Mapping
#### [MODIFY] [yfinance_provider.py](file:///G:/TradeMindAI-main/TradeMindAI-main/backend/infrastructure/repositories/yfinance_provider.py)
- Update `_map_symbol` to include the verified 2026 transition table:
    - `ZOMATO` -> `ETERNAL.NS`
    - `PEL` -> `PIRAMALFIN.NS`
    - `TATAMOTORS` -> `TMCV.NS`
    - `GMRINFRA` -> `GMRAIRPORT.NS`
    - `L&TFH` -> `LTF.NS`
- This ensures historical continuity for these major constituents.

### 2. Strict Validation Gate
#### [MODIFY] [validate_historical.py](file:///G:/TradeMindAI-main/TradeMindAI-main/scripts/universe/validate_historical.py)
- Introduce granular statuses: `COMPLETE`, `VALID_SHORT_HISTORY`, `PARTIAL`, `DATA_UNAVAILABLE`, `FAILED`.
- Logic Update:
    - `GUJGASLTD`: Classify as `VALID_SHORT_HISTORY` (listing data only available from July 2026).
    - `LTIM`: If genuinely unavailable after one last retry, mark `DATA_UNAVAILABLE` with documented reason.
- Exit Code: Return `1` if any `FAILED` stocks exist.

### 3. Probability Calibration
#### [MODIFY] [data_platform.py](file:///G:/TradeMindAI-main/TradeMindAI-main/backend/domain/models/data_platform.py)
- Add `calibration_params` field to `ModelMetadata`.
#### [MODIFY] [ml_service.py](file:///G:/TradeMindAI-main/TradeMindAI-main/backend/services/ml_service.py)
- Implement **Platt Scaling**:
    1. Split data into `Train (60%)`, `Calibrate (20%)`, `Test (20%)`.
    2. Fit Random Forest on Train.
    3. Fit Logistic Regression on probability scores using the Calibrate fold.
    4. Store calibration coefficients in the registry.
- Update `predict_with_champion` to apply calibration before returning confidence.

### 4. Documentation & Audit
#### [NEW] [PROBABILITY_CALIBRATION_REPORT.md](file:///G:/TradeMindAI-main/TradeMindAI-main/docs/PROBABILITY_CALIBRATION_REPORT.md)
- Summary of Brier Score, Log Loss, and reliability diagrams.
#### [MODIFY] [NIFTY200_HISTORICAL_COVERAGE_REPORT.md](file:///G:/TradeMindAI-main/TradeMindAI-main/docs/NIFTY200_HISTORICAL_COVERAGE_REPORT.md)
- Reflect recovered status (199/200 stocks).
#### [MODIFY] [P0_QUANT_AUDIT.md](file:///G:/TradeMindAI-main/TradeMindAI-main/docs/P0_QUANT_AUDIT.md)
- Update with final data status and zero-worker verification.

---

## Verification Plan

### Automated Tests
- `01B_validate_historical.ps1`: Must return SUCCESS after recovery.
- `scripts/ml/test_calibration.py`: New script to verify Brier score improvement.

### Manual Verification
- Inspect `historical_prices` for `ETERNAL` (Zomato) to ensure >500 rows.
- Verify `backend/ml/registry/` metadata contains calibration coefficients.
- Run `02_process_intelligence.ps1` and confirm it proceeds ONLY if gate is PASS/PARTIAL.
