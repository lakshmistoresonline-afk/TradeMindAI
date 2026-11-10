# Phase 3.2.28 Regression Results Report

**Date**: 2026-11-03  
**Status**: **100% PASSED** (322 backend unit tests + Web build)

## Automated Test Command Execution

| Test Suite | Command | Result | Total Tests | Duration | Exit Code |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **PostgreSQL Migration CLI** | `python -m pytest backend/tests/unit/test_postgres_migration_cli.py -v` | **PASSED** | 4 | 0.47s | 0 |
| **Ledger & Lifecycle** | `python -m pytest backend/tests/unit/test_phase7d_idempotency_and_lifecycle.py -v` | **PASSED** | 8 | 6.57s | 0 |
| **Ledger Contract** | `python -m pytest backend/tests/unit/test_signal_ledger_contract.py -v` | **PASSED** | 4 | 0.81s | 0 |
| **Data Quality Gate** | `python -m pytest backend/tests/unit/test_data_quality_gate.py -v` | **PASSED** | 24 | 43.00s | 0 |
| **Intraday Ingestion** | `python -m pytest backend/tests/unit/test_intraday_ingestion.py -v` | **PASSED** | 3 | 1.19s | 0 |
| **Transaction Safety** | `python -m pytest backend/tests/unit/test_ingestion_transaction_safety.py -v` | **PASSED** | 22 | 59.30s | 0 |
| **Full Backend Suite** | `python -m pytest backend/tests/unit/ -v` | **PASSED** | 322 (2 skipped) | 262.90s | 0 |
| **Frontend Web Build** | `cd web; npm run build` | **PASSED** | 2,488 modules | 13.05s | 0 |
| **Git Format Check** | `git diff --check` | **PASSED** | N/A | 0.05s | 0 |
