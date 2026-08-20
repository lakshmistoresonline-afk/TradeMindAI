# Implementation Plan - Fix Historical Data Pipeline before Step 4

This plan addresses the failures in the historical data pipeline to ensure a trustworthy dataset for the Step 4 master quantitative validation. We will resolve database routing issues, repair schema mismatches in Neon PostgreSQL, and complete the synchronization of missing histories.

## User Review Required

> [!IMPORTANT]
> **DATABASE ROUTING:** We will implement an explicit `TRADEMIND_EXECUTION_MODE=local` environment variable to force the system to use the local SQLite database for historical synchronization and backtesting. This prevents accidental targeting of the incomplete Neon database.
>
> **NEON SCHEMA REPAIR:** We identified that `historical_prices.source` and `open_interest` are incorrectly typed as `JSON` in Neon PostgreSQL. We will create a script to repair this schema to prevent `psycopg2` errors.
>
> **DATA COMPLETENESS:** We will re-run synchronization for GUJGASLTD, TATAMOTORS, and PEL in LOCAL mode to ensure they have sufficient history (>1000 candles) for valid indicator calculation.

## Proposed Changes

### 1. Database Routing Hardening
#### [MODIFY] [postgres.py](file:///G:/TradeMindAI/backend/core/postgres.py)
- Respect `TRADEMIND_EXECUTION_MODE=local` to force `DATABASE_URL` to local SQLite.
- Maintain production fail-closed protection.

### 2. Neon Schema Remediation
#### [NEW] [repair_neon_historical_schema.py](file:///G:/TradeMindAI/scripts/maintenance/repair_neon_historical_schema.py)
- Executes `ALTER TABLE` commands on Neon to correct column types:
    - `source`: `JSON` -> `VARCHAR(50)`
    - `open_interest`: `JSON` -> `BIGINT`
    - `indicators`: `TEXT` -> `JSONB` (if possible, or keep as text for consistency)

### 3. Pipeline Recovery
#### [RUN] Data Synchronization
- Execute `scripts/data/sync_market_history.py` for failing symbols:
    - GUJGASLTD, TATAMOTORS, PEL.
- Target: Local SQLite.

## Verification Plan

### Data Integrity Audit
- [ ] **Database Routing:** Verify `TRADEMIND_EXECUTION_MODE=local` avoids Neon.
- [ ] **GUJGASLTD Repair:** Confirm >1000 rows in SQLite after sync.
- [ ] **LTIM Exclusion:** Confirm LTIM remains at 0 rows (documented as unavailable).
- [ ] **Count Reconciliation:** Produce a final report of unique symbols (199 target) and candles.

### Final Acceptance Table (Post-Execution)
| Symbol | Expected Rows | Actual Rows | Status |
| :--- | :--- | :--- | :--- |
| **GUJGASLTD** | >1000 | TBD | `PENDING` |
| **TATAMOTORS** | >1000 | TBD | `PENDING` |
| **PEL** | >1000 | TBD | `PENDING` |
| **LTIM** | 0 | 0 | `EXCLUDED` |

---
**Verdict:** STEP 4 will remain **BLOCKED** until this audit reports `STEP4_READY`.
