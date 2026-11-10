# TradeMindAI — Phase 5.18 Transaction Ownership Audit Report

## 1. Overview & Transaction Contract Definition

This audit establishes the transaction ownership boundaries across `SignalLedgerService` and `EquitySignalGenerationService`.

### Transaction Ownership Rules
1. **Internally Created Sessions (`session is None`)**:
   - `SignalLedgerService._create_signal_internal()` opens `db = SessionLocal()`, inserts `db_signal`, executes `db.commit()`, and closes `db` in `finally:`.
   - Primary database transaction is committed internally, returning status `PERSISTED_AND_COMMITTED`.
   - Secondary Firestore mirroring executes post-commit.

2. **Caller-Owned Sessions (`session is not None`)**:
   - `SignalLedgerService._create_signal_internal()` uses `db = session` without committing or closing the session.
   - Executes `db.flush()`, returning status `PENDING_CALLER_COMMIT`.
   - Secondary Firestore mirroring is deferred (`mirror_status: "DEFERRED_UNTIL_CALLER_COMMIT"`), ensuring no orphan Firestore documents exist if the caller rolls back the transaction.
   - The caller retains complete transaction ownership to commit (`session.commit()`) or rollback (`session.rollback()`).

---

## 2. Call Graph & Lifecycle Mapping

```text
[Caller / Test Orchestrator]
       │
       ├── Creates Caller Session (e.g. TestSession / SessionLocal)
       │
       ▼
[EquitySignalGenerationService.generate_signal_for_symbol(session=caller_session)]
       │
       ├── 1. Validate Instrument Identity
       ├── 2. Build Time-Safe Feature Vector (DuckDB)
       ├── 3. Retrieve Exact Champion Model
       ├── 4. Generate Candidate Signal (SignalEngine)
       ├── 5. Validate Quality Gate & BUY Eligibility
       ├── 6. Validate Risk Geometry (SignalValidatorService)
       │
       ▼
[SignalLedgerService.persist_signal(signal, session=caller_session)]
       │
       ├── Detects `is_caller_session = True`
       ├── Inserts LiveSignalDB into caller's session
       ├── Executes `db.flush()` (Writes to DB buffer without committing or closing session)
       ├── Defers secondary Firestore mirroring (`mirror_status: "DEFERRED_UNTIL_CALLER_COMMIT"`)
       └── Returns `status: "PENDING_CALLER_COMMIT"`
       │
       ▼
[EquitySignalGenerationService.generate_signal_for_symbol()]
       │
       ├── Executes `caller_session.flush()`
       ├── Performs in-session readback query (`SignalLedgerService.get_signal(session=caller_session)`)
       │   └── Verifies non-null finite prices & all 9 required fields before returning candidate
       │
       ▼
[Caller / Test Orchestrator]
       │
       ├── Retains Transaction Ownership
       ├── Executes `caller_session.commit()` / `caller_session.rollback()` & `caller_session.close()`
       │
       ▼
[Post-Commit Secondary Mirror: SignalLedgerService.mirror_signal_after_commit(signal)]
       │
       └── Mirrors to Firestore ONLY AFTER database commit succeeds (`mirror_status: "SUCCESS"`)
```

---

## 3. Verification & Compliance Verdict

- **Transaction Ownership**: 100% compliant with ACID guarantees and caller boundary preservation.
- **Verdict**: **`PASS`**
