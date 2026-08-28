# Step 4.5.18: Async Firestore Mirror Recovery Report

**Date:** 2026-08-24
**Market Status:** OPEN
**Authoritative Store:** Neon PostgreSQL
**Mirror Store:** Google Firestore (Secondary / Best-Effort)

## 1. Architectural Stability
The live production path has been hardened to ensure that Firestore failures or quota exhaustion cannot interrupt the Shadow engine or the Dashboard visibility.

| Component | Technology | Primary Role | Status |
| :--- | :--- | :--- | :--- |
| **Shadow Engine** | Local Node | Logic & Persistence | RUNNING |
| **Operational DB** | Neon PostgreSQL | Authoritative Store | ONLINE |
| **Mirror DB** | Firestore | Analytics & Console Visibility | MIRRORING |
| **API Layer** | FastAPI (Railway) | Serving SQL Data | STABLE |

## 2. Mirror Implementation Features
- **Asynchronous & Non-Blocking:** Firestore writes are wrapped in `asyncio.wait_for` with a 30s timeout to prevent process hangs.
- **Quota Resilience:** Catching `ResourceExhausted` (429) errors and triggering a 1-hour cooldown period to allow quota reset.
- **Incremental Sync (Watermark):** Tracking `last_signal_ts` and `last_diag_ts` in `backend/data/shadow_sync_state.json` to prevent bulk rewrites.
- **Batch Processing:** Using Firestore batches for signal and diagnostic synchronization.
- **Idempotency:** Document IDs are deterministic (e.g., `sig_ID` and `diag_SYMBOL`) to prevent duplication.

## 3. Reconciliation Pass
| FIELD | NEON (Authoritative) | FIRESTORE (Mirror) | API (RC5.2) | DASHBOARD | PASS/FAIL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Market Status | OPEN | **OPEN** | OPEN | OPEN | PASS |
| Equity | 1002800.0 | **1002800.0** | 1002800.0 | 1,002,800 | PASS |
| Active Signals | 0 | **0** | `[]` | NONE | PASS |
| Hist. Signals | 2 | **2** | 2 | 2 | PASS |

## 4. Maintenance & Cleanup
- **`tiny_scan.py`:** Removed from scratch directory.
- **`ShadowSyncService.py`:** Refactored for async best-effort operation.
- **`shadow_service.py`:** Updated to call sync non-blockingly.

---

**FINAL VERDICT:** STEP_4_5_18_ASYNC_FIRESTORE_MIRROR_VERIFIED
The system is running with Neon PostgreSQL as the authoritative source. Firestore is successfully restored as a resilient, asynchronous secondary mirror that provides visibility in the Firebase Console without risking engine stability.
