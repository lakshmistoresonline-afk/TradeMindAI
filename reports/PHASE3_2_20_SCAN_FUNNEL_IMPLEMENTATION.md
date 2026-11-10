# Phase 3.2.20 Scan Funnel Implementation Report

**Date**: 2026-11-03  
**Target File**: [backend/services/equity_signal_generation_service.py](file:///D:/TradeMindAI/backend/services/equity_signal_generation_service.py)  
**Status**: **100% IMPLEMENTED & VERIFIED**

## Scan Funnel Metrics & Accounting

- `source_symbol_count`: Total validated NSE equity symbols (500).
- `symbols_attempted`: Total symbol/timeframe scan attempts.
- `candidate_buy_count`: Eligible candidate BUY signals generated.
- `rejected_non_buy`: Non-BUY candidates rejected by eligibility policy.
- `signals_persisted`: Newly inserted database records (`inserted == True`).
- `duplicates_prevented`: Pre-existing active signals (`status == "DUPLICATE_PREVENTED"`).
- `persistence_failures`: Database write exceptions (`status == "PERSISTENCE_FAILED"`).
