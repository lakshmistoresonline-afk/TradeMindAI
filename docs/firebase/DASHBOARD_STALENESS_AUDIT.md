# DASHBOARD STALENESS AUDIT - RESOLVED

## Staleness Remediation
- **Date:** 2026-08-22
- **Action:** Refactored `backend/api/v1/endpoints/shadow.py` to read from Firestore project `com-webcraft-trademindai-c8f75`.
- **Result:** Dashboard now displays real-time data from Firebase instead of stale SQL records from 2026-08-18.

## SBIN Signal Forensic - CLOSED
- **Signal ID:** `sig_SBIN_202608180715`
- **Initial Issue:** Displayed as ACTIVE (stale).
- **Actual State:** TARGET_HIT (WIN).
- **Resolution:** The API now correctly filters signals by `status == 'ACTIVE'`. Since SBIN is marked as `TARGET_HIT` in Firestore, it is correctly omitted from the active signals table.

## Hardcoded Baseline Removal
- **Baseline Start:** Now fetched dynamically from `shadow_summary/latest.baseline_start`.
- **Fallback:** Returns `null` if the field is missing, preventing misleading historical dates.

## Cache Remediation
- Added manual "REFRESH" button to the UI to bypass browser/client-side caching.
- Diagnostics section now displays "CLIENT FETCH TS" to verify freshness.
