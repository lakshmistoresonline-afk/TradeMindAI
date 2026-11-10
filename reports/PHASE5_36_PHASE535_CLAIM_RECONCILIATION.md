# TradeMindAI — Phase 5.36 Phase 5.35 Evidence Reconciliation Report

## 1. Evidence Audit & Reclassification

### Discrepancy Reconciliations
1. **Test Count Reconciliations**:
   - `test_phase5_signal_pipeline.py`: **12 passed**.
   - `test_signal_ledger_transaction_ownership.py`: **12 passed**.
   - `test_phase942_end_to_end_proof.py`: **3 passed**.
   - Combined 8-file regression suite: **86 passed**.
   - Full repository unit suite (`backend/tests/unit/`): **329 passed** (2 skipped).
   - **Verdict**: All test numbers reflect different suite scopes and reconcile 100%.

2. **Frontend Production Build**:
   - Compiles cleanly (`App.tsx` & `EquitySignals.tsx` clean, 0 TypeScript/React errors).

3. **Transaction Ownership**:
   - Caller sessions flush (`db.flush()`) without committing or closing. Status: `PENDING_CALLER_COMMIT`.
   - Internal sessions commit (`db.commit()`) and close in `finally:`. Status: `PERSISTED_AND_COMMITTED`.
