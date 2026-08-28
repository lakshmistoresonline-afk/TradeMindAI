# Step 4.5.20: Firestore Mirror Timestamp & P&L Precision Report

**Date:** 2026-08-24
**Status:** STEP_4_5_20_MIRROR_PRECISION_VERIFIED

## 1. Timestamp Interpretation & Mirror Lag
The reported "Mirror Lag" has been reconciled based on the following definitions:

| Timestamp Field | Meaning | Last Value (UTC) |
| :--- | :--- | :--- |
| **Latest Source TS** | The start time of the last successful authoritative NSE scan (Neon `shadow_events`). | 2026-08-24 06:25:07 |
| **Latest Mirror TS** | The completion time of the last best-effort mirror sync to Firestore (`last_run`). | 2026-08-24 07:37:25 |
| **Actual Mirror Lag** | The difference between Sync Completion and the state it reflects. | ~72 minutes |

> [!NOTE]
> The mirror lag is currently higher than expected because the local Shadow engine is experiencing timeouts during the NIFTY 200 scan, delaying the creation of fresh authoritative state in Neon. The sync service is mirroring the last known stable state.

## 2. P&L Precision Correction
A discrepancy of ₹0.01 was identified between the authoritative Neon source and the Firestore mirror.

- **Root Cause:** Floating-point division in the P&L calculation (`allocation * (r / 100.0)`) resulted in `2799.9999999999995` which was truncated/rounded to `2799.99` in some views.
- **Correction:** Implemented explicit `round(..., 2)` in `ShadowSyncService.py` for all monetary P&L and equity fields.
- **Verification:** 
  - Authoritative Neon: ₹2,800.00
  - Mirrored Firestore: ₹2,800.00
  - **Result: PASS**

## 3. Authoritative State Recheck
| FIELD | NEON (SQL) | FIRESTORE (Mirror) | MATCH |
| :--- | :--- | :--- | :--- |
| Market Status | `OPEN` | `OPEN` | **YES** |
| Equity | `1002800.0` | `1002800.0` | **YES** |
| Realized P&L | `2800.0` | `2800.0` | **YES** |
| Active Signals | 0 | 0 | **YES** |

---

**FINAL VERDICT:** STEP_4_5_20_MIRROR_PRECISION_VERIFIED
Accounting precision is now consistent across all tiers. Timestamp meanings are documented, and the mirror lag reflects the age of the last successfully recorded authoritative scan.
