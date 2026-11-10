# Phase 3.2.20 Regression Results Report

**Date**: 2026-11-03  
**Status**: **100% PASSED** (318 backend unit tests + Web build)

## Automated Regression Command Results

| Test Suite | Command | Result | Total Tests | Duration | Exit Code |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Ledger & Lifecycle** | `python -m pytest backend/tests/unit/test_phase7d_idempotency_and_lifecycle.py -v` | **PASSED** | 8 | 10.62s | 0 |
| **Ledger Contract** | `python -m pytest backend/tests/unit/test_signal_ledger_contract.py -v` | **PASSED** | 4 | 0.65s | 0 |
| **Data Quality Gate** | `python -m pytest backend/tests/unit/test_data_quality_gate.py -v` | **PASSED** | 24 | 60.16s | 0 |
| **Intraday Ingestion** | `python -m pytest backend/tests/unit/test_intraday_ingestion.py -v` | **PASSED** | 3 | 1.67s | 0 |
| **Transaction Safety** | `python -m pytest backend/tests/unit/test_ingestion_transaction_safety.py -v` | **PASSED** | 22 | 79.72s | 0 |
| **Full Backend Suite** | `python -m pytest backend/tests/unit/ -v` | **PASSED** | 308 (2 skipped) | 321.75s | 0 |
| **Frontend Web Build** | `cd web; npm run build` | **PASSED** | 2,488 modules | 41.79s | 0 |
| **Git Format Check** | `git diff --check` | **PASSED** | N/A | 0.05s | 0 |
