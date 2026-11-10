# Phase 4.2 Global Quality Gate Reconciliation Report

**Date**: 2026-11-03  
**Target File**: [backend/services/data_quality_service.py](file:///D:/TradeMindAI/backend/services/data_quality_service.py)

## Global Data Quality Gate Status

- **Evaluation Outcome**: `signal_generation_allowed = False`
- **Global Data Status**: `DEGRADED_UNSUPPORTED`
- **Constituent Status Breakdown**:
  - `PASS`: **356** stocks (100% complete daily and intraday 5m OHLCV)
  - `PARTIAL`: **143** stocks (47 post-2015 IPO listing boundaries + 96 equities with minor 5m volume gaps)
  - `UNSUPPORTED`: **1** stock (`BAGMANE`)
- **Fail-Closed Lock**: `EquitySignalGenerationService.run_production_scan()` halts immediately when `signal_generation_allowed == False`.
