# TradeMindAI — Phase 5.34 Phase 5.33 Evidence Reconciliation Report

## 1. Discrepancy Forensic Audit & Reclassification

### Item 1: Test Count Reconciliations
- **Targeted Unit Test Suite** (`test_phase5_signal_pipeline.py`): **12 tests**.
- **Dedicated Transaction Ownership Suite** (`test_signal_ledger_transaction_ownership.py`): **12 tests**.
- **Phase 9.4.2 Integration Proof Suite** (`test_phase942_end_to_end_proof.py`): **3 tests**.
- **Combined 8-File Unit Suite**: **86 collected test cases**.
- **Full Repository Backend Suite** (`backend/tests/unit/`): **329 collected test cases** (329 passed, 2 skipped).
- **Classification**: **`VERIFIED BY EXECUTED TEST`** (Test totals reconcile 100% depending on module filter).

### Item 2: Historical Provenance Claims vs Manifest Hashes
- **Working-Tree Byte Integrity**: Working-tree files match committed HEAD `a97300dcd766` **100%** byte-for-byte.
- **Historical Provenance**: Relative to original 2026-09-11 manifest baseline hashes, `risk.py` matches 100%, while `signal_engine.py`, `outcome_engine.py`, `risk_engine.py`, and `config.py` reflect pre-HEAD baseline commits.
- **Classification**: **`PARTIAL — HISTORICAL BASELINE RECONCILIATION REQUIRED`** (HEAD integrity is 100% verified; historical provenance recorded as partial).

### Item 3: Secondary Firestore Mirror Delivery
- **Source Inspection**: `SignalLedgerService._create_signal_internal()` defers secondary Firestore mirroring for caller sessions (`mirror_status: "DEFERRED_UNTIL_CALLER_COMMIT"`), preventing orphan Firestore documents if caller rolls back.
- **Classification**: **`VERIFIED FROM SOURCE`** (Non-blocking secondary mirror lifecycle operates as designed).

### Item 4: Readback & Session Boundary
- **Source Inspection**:
  - Internally owned sessions (`session is None`) open a distinct `readback_session = SessionLocal()`, query the record, verify 9 fields, and close `readback_session`.
  - Caller-owned sessions (`session is not None`) execute `db.flush()` and verify in-session pending records without committing or closing caller's session.
- **Classification**: **`VERIFIED FROM SOURCE`** (Session boundaries accurately distinguished).
