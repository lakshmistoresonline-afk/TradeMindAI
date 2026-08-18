# Task Checklist - Phase 5H: Hosted Shadow Monitoring Dashboard

- `[/]` Backend & API Development
    - `[ ]` Create `backend/api/v1/endpoints/shadow.py`
    - `[ ]` Register shadow router in `backend/api/v1/api.py`
    - `[ ]` Implement `ShadowSyncService` in `backend/services/shadow_sync_service.py`
    - `[ ]` Integrate sync into `ShadowService.run_shadow_cycle()`
- `[ ]` Frontend Implementation
    - `[ ]` Create `web/src/pages/ShadowMonitor.tsx`
    - `[ ]` Add `/shadow` route to `web/src/App.tsx`
    - `[ ]` Implement "Shadow Monitor" Sidebar link in `web/src/components/Layout.tsx`
- `[ ]` Security & Verification
    - `[ ]` Verify Read-Only API constraints
    - `[ ]` Perform forensic check for secret exposure in Firestore payload
    - `[ ]` Test data freshness sync (30-60s)
- `[ ]` Deployment & Reporting
    - `[ ]` Push changes to Git
    - `[ ]` Generate Deplayment Report `PHASE5H_WEB_MONITOR_DEPLOYMENT_REPORT.md`
