# PHASE 6: SHADOW DATABASE MIGRATION

## 1. Migration Overview
- **Source:** Local SQLite `backend/local_operational.db`
- **Target:** Hosted PostgreSQL (Neon)
- **Baseline:** Phase 5G (2026-08-18)
- **Strategy:** Frozen v2.2

## 2. Records Migrated
| Table | Record Count | Criteria |
| :--- | :--- | :--- |
| `shadow_signals` | 2 | All Phase 5G baseline signals. |
| `shadow_events` | 1800 | All Phase 5G evaluation cycles. |

## 3. Evidence Verification
- **SBIN Outcome:** `TARGET_HIT` (WIN)
- **Net Return:** +2.80%
- **Status:** **VERIFIED**

## 4. Signal Consistency Audit
- **Signal ID:** `sig_SBIN_202608180715` (Resolved)
- **Signal ID:** `sig_SBIN_202608181011` (Active)
- **Checksums:** All timestamps and probabilities matched source exactly.

## 5. Migration Logic
The script [migrate_shadow_to_pg.py](file:///G:/TradeMindAI/scripts/maintenance/migrate_shadow_to_pg.py) uses an append-only logic that:
1. Filters records by the 2026-08-18 baseline.
2. Deduplicates against existing PG records using the unique `signal_id`.
3. Verifies terminal outcome persistence in the target tier.

## 6. Rollback Procedure
If target data is corrupted:
1. Truncate `shadow_signals` and `shadow_events` in PostgreSQL.
2. Re-run migration script from the local authoritative SQLite backup.

## Final Status
`MIGRATION_READY_FOR_DEPLOYMENT`
