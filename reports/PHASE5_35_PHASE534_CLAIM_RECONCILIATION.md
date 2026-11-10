# TradeMindAI — Phase 5.35 Evidence Reconciliation Report

## 1. Evidence Audit & Reclassification

### Discrepancy Reconciliations
1. **Executed Test Commands & Raw Output**:
   - `python -m pytest backend/tests/unit/test_phase5_signal_pipeline.py backend/tests/unit/test_signals_only_architecture_invariant.py backend/tests/unit/test_phase4_3_9_quality_and_pipeline.py backend/tests/unit/test_phase4_3_8_quality_and_pipeline.py backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py backend/tests/unit/test_quarantine_enforcement.py backend/tests/unit/test_postgres_migration_cli.py backend/tests/unit/test_signal_ledger_transaction_ownership.py -v`:
     - **Collected 86 items**: **86 PASSED, 0 FAILED** (39.71s, Exit code 0).
   - `python -m pytest backend/tests/integration/test_phase942_end_to_end_proof.py -v`:
     - **Collected 3 items**: **3 PASSED, 0 FAILED** (0.72s, Exit code 0).
   - `npx tsc --noEmit` in `D:/TradeMindAI/web`:
     - **Compilation result**: **Clean (0 errors, Exit code 0)**.

2. **Transaction Ownership**:
   - Caller sessions flush (`db.flush()`) without committing or closing. Status: `PENDING_CALLER_COMMIT`.
   - Internal sessions commit (`db.commit()`) and close in `finally:`. Status: `PERSISTED_AND_COMMITTED`.

3. **Firestore Secondary Mirroring**:
   - Deferred mirror status `DEFERRED_UNTIL_CALLER_COMMIT` for caller sessions.
   - Non-blocking post-commit execution via `mirror_signal_after_commit()`.
