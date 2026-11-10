# TradeMindAI — Master Readiness 04: Database & Transaction Audit Report

## 1. Transaction Ownership Contract

### Session Contract Matrix
1. **Caller-Owned Session (`session is not None`)**:
   - `_create_signal_internal()` & `update_signal()` execute `db.flush()` and `db.refresh()`.
   - Never commits, rolls back, or closes caller sessions.
   - Returns `PENDING_CALLER_COMMIT` or `True`.

2. **Internally Created Session (`session is None`)**:
   - Opens `db = SessionLocal()`, executes `db.commit()`, and closes `db` in `finally:`.
   - Returns `PERSISTED_AND_COMMITTED` or `True`.

---

## 2. Verdict
- **Transaction Safety**: **`PASS`**
