# Implementation Plan - Emergency Railway/Celery Worker Elimination

This plan implements a strict "Zero-Worker" policy on Railway to resolve production errors and move all background processing to local manual execution.

## User Review Required

> [!CRITICAL]
> **RAILWAY WORKER DEACTIVATION:** This change will disable all Celery Workers and Beat schedulers on Railway. Background tasks like market sync, ML training, and Shadow monitoring will no longer run automatically in the cloud.
>
> **LOCAL MANUAL EXECUTION:** All background processing must now be initiated manually from the local Windows PC using the provided scripts.

## Proposed Changes

### 1. Hardening Railway Startup Script
#### [MODIFY] [start.sh](file:///G:/TradeMindAI/backend/start.sh)
- Remove all logic for `worker`, `beat`, `shadow-worker`, and `shadow-beat`.
- Implement a strict check: If `SERVICE_TYPE` is not `api`, the script will log an error and exit immediately.
- This prevents Railway from starting any background execution roles even if configured.

### 2. Disabling Automated Schedule
#### [MODIFY] [tasks.py](file:///G:/TradeMindAI/backend/workers/tasks.py)
- Disable the `celery_app.conf.beat_schedule` entirely in production.
- Add a safety check in `celery_app` initialization to prevent it from starting as a worker/beat on Railway.

### 3. Documentation & Audit
#### [NEW] [RAILWAY_ZERO_WORKER_AUDIT.md](file:///G:/TradeMindAI/docs/RAILWAY_ZERO_WORKER_AUDIT.md)
- Document the removal of Railway workers and schedulers.
- List the local replacements for each previously automated task.

## Verification Plan

### Automated Verification
- **Local Test:** Verify that `SERVICE_TYPE=api` still starts the FastAPI server correctly.
- **Fail-Closed Test:** Set `SERVICE_TYPE=worker` locally and verify the script exits with an error.

### Manual Verification (Railway)
1. **Redeploy to Railway:** Apply the changes.
2. **Log Audit:** Confirm that any service other than the API shows "ERROR: Background workers are disabled on Railway."
3. **Task Audit:** Confirm that no new evaluation events or signals are created autonomously in Neon PostgreSQL.

## Success Criteria
- Railway Workers = 0
- Railway Schedulers = 0
- Railway Background Tasks = 0
- No `ModuleNotFoundError: No module named 'production'` on Railway.
- Local manual execution remains fully functional.
