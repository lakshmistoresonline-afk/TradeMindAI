# TradeMindAI — Master Readiness 02: Complete Defect Register

## 1. Consolidated Defect Inventory

| Defect ID | Severity | Component / Path | Description | Required Remediation | Safety / Isolation Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **DEF-001** | CRITICAL | `SignalLedgerService.update_signal()` | Calling `update_signal()` on terminal-state signals without immutability check can mutate core entry facts. | Restore fail-closed terminal-state immutability protection. | **Isolated** |
| **DEF-002** | HIGH | `SignalLedgerService.persist_signal()` | Deferred secondary Firestore mirror requires transactional outbox to guarantee delivery after commit. | Implement SQL outbox table and post-commit dispatcher helper. | **Isolated** |
| **DEF-003** | HIGH | `EquitySignalGenerationService` | Original candidate signal prices must be validated for finiteness/nulls before persistence. | Enforce non-null, finite (`np.isfinite()`), positive price geometry check. | **Isolated** |
| **DEF-004** | MEDIUM | `test_phase5_signal_pipeline.py` | Need dedicated adversarial unit tests for NaN price input injection and outbox delivery. | Implement adversarial test suite in `test_phase5_signal_pipeline.py`. | **Isolated** |

---

## 2. Risk & Impact Summary

All findings are remediable within isolated test database boundaries without altering frozen strategy V2.2 core files or runtime safety invariants.
