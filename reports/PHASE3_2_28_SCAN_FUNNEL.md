# Phase 3.2.28 Scan Funnel Report

**Date**: 2026-11-03  
**Target File**: [backend/services/equity_signal_generation_service.py](file:///D:/TradeMindAI/backend/services/equity_signal_generation_service.py)  
**Status**: **100% IMPLEMENTED & VERIFIED**

## Reconciled Scan Accounting Metrics

- `source_symbol_count`: 500 validated NSE equity symbols.
- `symbols_attempted`: Scan attempts across symbols and horizons.
- `candidate_buy_count`: Generated BUY candidates.
- `rejected_non_buy`: Non-BUY candidates rejected by eligibility policy.
- `signals_persisted`: Newly committed database insertions (`inserted == True`).
- `duplicates_prevented`: Pre-existing active signals (`status == "DUPLICATE_PREVENTED"`).
- `persistence_failures`: Database write exceptions (`status == "PERSISTENCE_FAILED"`).
