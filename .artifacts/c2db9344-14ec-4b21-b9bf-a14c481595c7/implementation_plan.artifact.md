# Implementation Plan: TradeMind AI Quantitative Validation (Real-Data)

Move TradeMind AI from **PRODUCTION ARCHITECTURE READY** to **REAL-DATA QUANTITATIVELY VALIDATED / EVIDENCE-BACKED**.

## User Review Required

> [!IMPORTANT]
> **F&O Historical Data Gap**: The current database has zero historical price records for F&O instruments. Real historical F&O validation is blocked until this data is ingested. I will implement the ingestion logic, but it depends on the configured market data provider (Groww) having this data available.

> [!WARNING]
> **LTIM Discrepancy**: LTIMindtree (LTIM) is part of the canonical NIFTY 200 but is missing from historical data. I will attempt to locate it or document it as a known provider limitation.

## Proposed Changes

### 1. Data Engineering & Universe Validation

#### [MODIFY] [validate_historical.py](file:///D:/TradeMindAI/scripts/universe/validate_historical.py)
*   Update to generate the detailed machine-readable **Universe/Data Coverage Report** (CSV/JSON/Markdown).
*   Add logic to check for corporate actions (splits/bonuses) if possible.

#### [NEW] [generate_universe_report.py](file:///D:/TradeMindAI/scripts/universe/generate_universe_report.py)
*   A dedicated script to produce the comprehensive report required in Step 2 of the objective.

#### [MODIFY] [ingestion_service.py](file:///D:/TradeMindAI/backend/services/ingestion_service.py)
*   Enhance to handle F&O historical OHLC ingestion if supported by the provider.

---

### 2. Quantitative Engines & Validation

#### [MODIFY] [signal_engine.py](file:///D:/TradeMindAI/backend/services/signal_engine.py)
*   Implement real `data_quality_score` calculation based on freshness and coverage.

#### [MODIFY] [calibration_service.py](file:///D:/TradeMindAI/backend/services/calibration_service.py)
*   Remove hardcoded Platt Scaling parameters where they conflict with model-derived values.
*   Make slippage/cost assumptions configurable.

#### [MODIFY] [scoring_service.py](file:///D:/TradeMindAI/backend/services/scoring_service.py)
*   Remove hardcoded "STABLE/HIGH/STRONG" labels; derive from data.

---

### 3. Master Validation & Reporting

#### [MODIFY] [04_run_validation.ps1](file:///D:/TradeMindAI/scripts/windows/04_run_validation.ps1)
*   Orchestrate the complete pipeline: Universe -> Coverage -> Integrity -> Leakage -> Model -> Calibration -> EV -> No-Trade -> Backtest.
*   Integrate the generation of `QUANTITATIVE_VALIDATION_FINAL_REPORT.md` and `validation/results/quant_validation_results.json`.

#### [NEW] [quant_validator.py](file:///D:/TradeMindAI/scripts/accuracy/quant_validator.py)
*   Core Python engine for out-of-sample validation and metric calculation.

---

### 4. Production Safety & UI

#### [MODIFY] [MarketCommandCenter.tsx](file:///D:/TradeMindAI/web/src/pages/MarketCommandCenter.tsx)
*   Replace hardcoded exposure and return values with live data from the backend.

#### [MODIFY] [RiskGuard.tsx](file:///D:/TradeMindAI/web/src/pages/RiskGuard.tsx)
*   Replace mock holdings and hardcoded risk scores with real portfolio data.

#### [MODIFY] [SignalValidation.tsx](file:///D:/TradeMindAI/web/src/pages/StrategyBuilder/SignalValidation.tsx)
*   Ensure calibration charts use real backend data instead of defaults.

## Verification Plan

### Automated Tests
*   `pytest backend/tests/unit/test_validation_logic.py` (To be created)
*   `python scripts/universe/validate_historical.py`
*   `scripts/windows/04_run_validation.ps1`

### Manual Verification
*   Inspect `docs/NIFTY200_HISTORICAL_COVERAGE_REPORT.md` for completeness.
*   Inspect `QUANTITATIVE_VALIDATION_FINAL_REPORT.md` for evidence of real-data validation.
*   Verify UI displays real metrics by checking API responses in the browser.
