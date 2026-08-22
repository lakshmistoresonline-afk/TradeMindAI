# Shadow Dashboard Forensic Fix Implementation Plan

The Shadow Dashboard at `/shadow` is currently showing stale, mock, or cached data from 2026-08-18. This is because the backend API reads from a local/stale SQL database instead of the authoritative Firebase/Firestore source. This plan refactors the backend to use Firestore and updates the UI to reflect real-time application state.

## User Review Required

> [!IMPORTANT]
> The backend will be switched to read exclusively from Firestore for Shadow Monitor endpoints. Ensure that the `FIREBASE_SERVICE_ACCOUNT` environment variable or `service-account.json` is correctly configured in the production (Railway) environment.

> [!WARNING]
> The "SBIN" record currently appearing as `ACTIVE` will be investigated in Firestore. If it is found to be stale (already resolved in local engine), it will be corrected in Firebase to ensure the dashboard remains accurate.

## Proposed Changes

### Backend API Refactor

Modify `backend/api/v1/endpoints/shadow.py` to fetch data from Firestore.

#### [MODIFY] [shadow.py](file:///G:/TradeMindAI/backend/api/v1/endpoints/shadow.py)
- Import `db_client` from `backend.core.database`.
- Refactor `/status`, `/summary`, `/active-signals`, `/performance`, `/universe`, and `/health` to query Firestore collections:
    - `shadow_summary/latest`
    - `shadow_signals`
    - `shadow_scan_diagnostics`

### Frontend UI Enhancements

Update `web/src/pages/ShadowMonitor.tsx` to improve transparency and data freshness.

#### [MODIFY] [ShadowMonitor.tsx](file:///G:/TradeMindAI/web/src/pages/ShadowMonitor.tsx)
- Replace "WORKER HB" with "LAST FIREBASE SYNC".
- Add a "REFRESH" button and "LAST UPDATED" timestamp.
- Add a "DIAGNOSTICS" section (collapsible/dev-only) showing the active API endpoint and Firebase project ID (Rule #20).

### Documentation & Audits

#### [NEW] [DASHBOARD_DATA_SOURCE_AUDIT.md](file:///G:/TradeMindAI/docs/firebase/DASHBOARD_DATA_SOURCE_AUDIT.md)
#### [NEW] [DASHBOARD_FIREBASE_MAPPING.md](file:///G:/TradeMindAI/docs/firebase/DASHBOARD_FIREBASE_MAPPING.md)
#### [NEW] [DASHBOARD_STALENESS_AUDIT.md](file:///G:/TradeMindAI/docs/firebase/DASHBOARD_STALENESS_AUDIT.md)
#### [NEW] [DASHBOARD_VERIFICATION_REPORT.md](file:///G:/TradeMindAI/docs/firebase/DASHBOARD_VERIFICATION_REPORT.md)

## Verification Plan

### Automated Verification
- Run `scripts/accuracy/verify_firebase_shadow.py` to ensure Firebase connectivity.
- Create a test script to compare backend API responses with direct Firestore queries.

### Manual Verification
- Deploy changes to the local environment and verify the `/shadow` dashboard against the Firestore console.
- Check "SBIN" status in the UI vs. Firebase.
- Verify that "Incognito" mode shows the same data as a normal session (cache check).
