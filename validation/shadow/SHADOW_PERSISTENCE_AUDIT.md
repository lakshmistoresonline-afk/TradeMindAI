# Shadow Persistence Audit

## 1. Inventory of Current State
- ** autoridad Source (Database):** `backend/local_operational.db` -> `shadow_signals` table.
- **Derived Logs (CSV):** `validation/shadow/shadow_observations.csv`.
- **Summary Metrics (JSON):** `validation/results/shadow_performance.json`.

### Quantitative Inventory
- **Signals in DB:** 1 (SBIN, LONG, ACTIVE)
- **Evaluations in CSV:** 200 (Single session)
- **Signals in JSON:** 1 (Consistent with DB)

## 2. Root Cause Analysis
The loss of previous Shadow signals was caused by **manual file-system operations** during infrastructure remediation.
1. **CSV Truncation:** The `shadow_observations.csv` was manually deleted to resolve a pandas parsing error. Since `generate_shadow_report.py` derived the session count and cumulative stats from the CSV, the reported history was reset.
2. **Database State:** The `shadow_signals` table currently contains only 1 record. Previous signals from Phase 5A/B are unrecoverable due to local database file swaps standardized during Phase 5C.

## 3. Data Integrity & Lifecycle Audit
- **Creation Path:** `ShadowService.persist_shadow_signal()` correctly checks for existing 'ACTIVE' signals before insertion.
- **Outcome Path:** `ShadowService.audit_open_signals()` updates status from 'ACTIVE' to 'TARGET_HIT', 'STOP_LOSS', or 'EXPIRED'.
- **Persistence Rules:** The system currently lacks a hard unique constraint on `(symbol, timestamp)` in the `shadow_signals` table, which could lead to duplicates if signal IDs are not stable.

## 4. Corrective Actions Required
- [ ] Implement `UNIQUE` constraint on `shadow_signals.id` (Authoritative Signal ID).
- [ ] Refactor `generate_shadow_report.py` to use the Database as the **Primary Source of Truth** for all cumulative metrics.
- [ ] Ensure all file writes to `shadow_observations.csv` use `mode='a'` (Append) without exception.
- [ ] Implement `SHADOW_RECOVERY_TEST` to verify survival across process restarts.
