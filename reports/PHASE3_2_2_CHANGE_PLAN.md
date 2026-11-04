# Phase 3.2.2 Change Plan

**Date**: 2026-11-03  
**Objective**: Non-destructive data quality verification, audit reports generation, and automated regression testing.

## Execution Sequence

1. **Read-Only Audit**: Complete code inspection of `data_quality_service.py` and test suites.
2. **NSE Calendar Evidence Report**: Generate `reports/PHASE3_2_2_NSE_CALENDAR_EVIDENCE.csv` and `reports/PHASE3_2_2_NSE_CALENDAR_AUDIT.md`.
3. **500-Symbol Reconciliation & Storage Audit**: Generate `reports/PHASE3_2_2_500_SYMBOL_RECONCILIATION.csv`, `reports/PHASE3_2_2_500_SYMBOL_SUMMARY.md`, `reports/PHASE3_2_2_STORAGE_RECONCILIATION.csv`, and `reports/PHASE3_2_2_STORAGE_AUDIT.md`.
4. **Live Global Gate Payload**: Execute read-only global evaluation and output `reports/PHASE3_2_2_GLOBAL_GATE_RAW.json` and `reports/PHASE3_2_2_GLOBAL_GATE_SUMMARY.md`.
5. **Automated Unit Testing**: Run full pytest suite (`test_data_quality_gate.py`, `test_intraday_ingestion.py`, `test_ingestion_transaction_safety.py`, and full backend suite) and `git diff --check`.
6. **Final Deliverable Generation**: Produce `reports/PHASE3_2_2_TEST_EXECUTION_REPORT.md` and `reports/PHASE3_2_2_FINAL_VERDICT.md`.
