# Implementation Plan - Phase 7.7: Fix Railway Beat Service Role

This phase resolves the role confusion in the Railway `trademind-beat` service. Forensic evidence shows that this service is currently starting a Celery Worker instead of the intended Celery Beat scheduler, resulting in zero autonomous shadow cycles.

## User Review Required

> [!IMPORTANT]
> **ROLE CORRECTION:** The `trademind-beat` service on Railway must have its `SERVICE_TYPE` environment variable corrected to `shadow-beat`.
>
> **ZERO-DUPLICATION:** This will stop the duplicate worker running on the beat service and activate the actual scheduler required for 24/7 monitoring.
>
> **STRATEGY FREEZE:** No trading logic or Strategy v2.2 parameters will be modified.

## Proposed Changes

### 1. Hardening Railway Startup Script
#### [MODIFY] [start.sh](file:///G:/TradeMindAI/backend/start.sh)
- Add explicit logging of the detected `SERVICE_TYPE` at the very beginning of the script to make future role confusion immediately visible in logs.
- Ensure `shadow-beat` does not attempt to use `concurrency` or `queue` flags which are worker-specific.

### 2. Schedule Validation
#### [MODIFY] [tasks.py](file:///G:/TradeMindAI/backend/workers/tasks.py)
- Add a startup log entry that prints the count of active schedules in `beat_schedule`. This helps verify the scheduler "sees" the Shadow cycle task upon boot.

### 3. Monitoring API Resilience
- No changes required. The API is already reading from Neon PG.

## Verification Plan

### Manual Verification (Cloud Logs)
1. **Apply Configuration:** Change `SERVICE_TYPE` to `shadow-beat` in the Railway dashboard for the `trademind-beat` service.
2. **Startup Audit:** Confirm logs show "Starting Shadow Celery Beat..." and **NOT** "mingle: searching for neighbors".
3. **Dispatch Audit:** Wait for the next 30-minute interval and confirm "Sending due task backend.workers.tasks.run_shadow_cycle_task" appears in the beat logs.
4. **Execution Audit:** Confirm the `trademind-worker` (the actual worker) logs "Task received: ...run_shadow_cycle_task".

## Success Criteria
- [ ] `trademind-beat` service runs as `celery beat`.
- [ ] No worker "mingle" messages appear in the beat service logs.
- [ ] **Evaluation Cycles** increments autonomously on the web dashboard.
