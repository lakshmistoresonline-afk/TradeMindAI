# TradeMindAI — Phase 5.18 Secondary Firestore Mirror Audit Report

## 1. Secondary Mirroring Architecture & Outbox Design

Secondary Firestore mirroring is non-blocking and auxiliary to the authoritative Neon/Postgres database ledger.

### Rules Enforced
1. **Deferred Delivery for Caller-Owned Transactions**:
   - When `SignalLedgerService.persist_signal(signal, session=caller_session)` executes, Firestore mirroring returns `mirror_status: "DEFERRED_UNTIL_CALLER_COMMIT"`.
   - Secondary documents are NOT written to Firestore until after the authoritative Postgres transaction has successfully committed.

2. **Post-Commit Delivery**:
   - `SignalLedgerService.mirror_signal_after_commit(signal)` runs after caller commits.
   - If Firestore mirroring fails due to network or service errors, `mirror_status` returns `"FAILED"` without rolling back or invalidating the committed Postgres record.

3. **Immediate Mirroring for Internal Sessions**:
   - When `session is None`, `_create_signal_internal()` commits the Postgres transaction first (`db.commit()`), and then executes secondary Firestore mirroring (`mirror_status: "SUCCESS"` or `"FAILED"`).

---

## 2. Verification Verdict

- **No Premature Mirroring**: Verified. Uncommitted caller transactions leave 0 orphan Firestore documents.
- **Rollback Safety**: Verified. Transaction rollbacks clean up local DB records and leave no secondary artifacts.
- **Verdict**: **`PASS`**
