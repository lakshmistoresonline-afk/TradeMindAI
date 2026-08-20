# Task Checklist - Fix Historical Data Pipeline

- `[x]` Database Routing & Backup
    - `[x]` Backup `backend/local_operational.db`
    - `[x]` Modify `backend/core/postgres.py` for `TRADEMIND_EXECUTION_MODE=local`
- `[x]` Neon Schema Repair
    - `[x]` Implement `repair_neon_historical_schema.py`
    - `[x]` Execute repair on Neon
- `[x]` Pipeline Recovery (SQLite)
    - `[x]` Sync GUJGASLTD (Local Mode)
    - `[x]` Sync TATAMOTORS (Local Mode)
    - `[x]` Sync PEL (Local Mode)
- `[x]` Final Audit & Reconciliation
    - `[x]` Generate `docs/DATA_PIPELINE_PRE_STEP4_AUDIT.md`
    - `[x]` Reconcile symbol/candle counts
    - `[x]` Set `STEP4_READY` verdict
