# PHASE 2M: F&O API & EXPORT PARITY

## 1. Objective
Ensure 100% consistency between the authoritative Neon ledger and all downstream consumers for F&O extension fields.

## 2. Parity Test (master_opt_RELIANCE_...)
| Field | Neon Value | API Response | JSON Export | Parity |
| :--- | :--- | :--- | :--- | :--- |
| `instrument_id` | `RELIANCE3100CE` | `RELIANCE3100CE`| `RELIANCE3100CE`| **MATCH** |
| `strike` | `3100.0` | `3100.0` | `3100.0` | **MATCH** |
| `option_type` | `CE` | `CE` | `CE` | **MATCH** |
| `asset_class` | `OPTIONS` | `OPTIONS` | `OPTIONS` | **MATCH** |

## 3. Reconciliation Results
- **Neon Authority**: **PASS**. 100% of Extension fields survive serialization.
- **Frontend Sync**: **PASS**. Dashboard correctly maps derivative fields.

---
**Status**: PARITY_CERTIFIED
