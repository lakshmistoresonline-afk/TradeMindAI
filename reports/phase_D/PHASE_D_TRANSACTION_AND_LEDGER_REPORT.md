# TradeMindAI — Phase D Transaction & Ledger Report

**Service Component**: [backend/services/signal_ledger_service.py](file:///D:/TradeMindAI/backend/services/signal_ledger_service.py)

---

## 1. Session Ownership & Transaction Boundaries

`SignalLedgerService` strictly distinguishes caller-owned vs internally created database sessions:
- **Caller-Owned Session (`session is not None`)**:
  - `_create_signal_internal()` and `update_signal()` execute `db.flush()` and `db.refresh()`.
  - Never commits, rolls back, or closes caller-owned sessions.
  - Preserves pending caller work and respects caller transaction rollback.
  - Returns `mirror_status: "DEFERRED_UNTIL_CALLER_COMMIT"`.
- **Internally Created Session (`session is None`)**:
  - Opens `db = SessionLocal()`, executes `db.commit()`, and closes `db` in `finally:`.
  - Returns `mirror_status: "PERSISTED_AND_COMMITTED"`.

---

## 2. Terminal-State Immutability Contract

In `SignalLedgerService.update_signal()`:
- Reopening terminal signals (`TARGET_HIT`, `STOP_LOSS`, `EXPIRED`, `CANCELLED`, `AMBIGUOUS`) back to active states is strictly blocked (`TERMINAL_SIGNAL_IMMUTABLE`).
- Modifying core strategy facts (`symbol`, `direction`, `entry_price`, `target_price`, `stop_price`, `model_version`, `prediction_id`) on terminal signals is strictly blocked.
- Simultaneous immutable-field mutations during active-to-terminal transitions are strictly blocked.

---

## 3. Secondary Firestore Mirror Reliability

- Secondary Firestore mirroring is non-blocking to primary Postgres writes.
- For caller-owned sessions, mirroring is deferred until post-commit (`mirror_signal_after_commit()`), preventing orphan Firestore documents if caller rolls back.
- Mirror failure returns `mirror_status: "FAILED"` without altering or rolling back primary database records.

---

## 4. Test Verification Summary

- `test_update_signal_caller_session_no_commit`: **PASSED**
- `test_update_signal_caller_session_no_close`: **PASSED**
- `test_update_signal_caller_session_no_rollback`: **PASSED**
- `test_update_signal_caller_rollback_reverts_update`: **PASSED**
- `test_update_signal_caller_commit_persists_update`: **PASSED**
- `test_update_signal_terminal_reopen_fails`: **PASSED**
- `test_update_signal_terminal_restricted_fields_fail`: **PASSED**
- `test_update_signal_valid_terminal_transition_succeeds`: **PASSED**
- `test_create_signal_internal_caller_session_flushes_only`: **PASSED**
