# Implementation Plan - Phase 7.5: Celery Routing & Production Reliability Fix

This phase resolves the remaining infrastructure defects identified in the Railway production logs: incorrect Celery queue routing, a missing Beat schedule for the Shadow cycle, and unstable database connection pooling.

## User Review Required

> [!IMPORTANT]
> **QUEUE CONSOLIDATION:** All production Shadow tasks and heartbeats will be strictly routed to the `shadow` queue. The Shadow Worker will be configured to ONLY listen to this queue, preventing it from wasting resources on generic tasks.
>
> **CONNECTION RESILIENCE:** We are enabling `pool_pre_ping=True` and `pool_recycle=3600` for the Neon PostgreSQL engine. This automatically detects and recovers "stale" SSL connections that previously caused 500 errors.
>
> **SECURITY HARDENING:** All diagnostic logging of Firebase credential lengths and metadata will be removed to prevent information leakage in production logs.

## Proposed Changes

### 1. Celery Routing & Schedule Repair
#### [MODIFY] [tasks.py](file:///G:/TradeMindAI/backend/workers/tasks.py)
- Refine `celery_app.conf.beat_schedule`:
    - Ensure `run-shadow-monitoring-cycle` correctly points to `backend.workers.tasks.run_shadow_cycle_task`.
    - Explicitly set `options={"queue": "shadow"}` for all scheduled tasks.
- Refine task decorators:
    - Ensure `terminal_heartbeat` is explicitly routed to `queue="shadow"`.

### 2. Database Connection Hardening
#### [MODIFY] [postgres.py](file:///G:/TradeMindAI/backend/core/postgres.py)
- Update `create_engine` for PostgreSQL to include:
    - `pool_pre_ping=True`: Verifies connection health before use.
    - `pool_recycle=3600`: Rotates connections every hour to prevent stale SSL timeouts.
    - `pool_size=10` and `max_overflow=20`: Optimized for Railway replica concurrency.

### 3. Railway Startup Refinement
#### [MODIFY] [start.sh](file:///G:/TradeMindAI/backend/start.sh)
- Ensure the `shadow-worker` service explicitly starts with `-Q shadow` to match the routing configuration.

### 4. Security & Firebase Isolation
#### [MODIFY] [database.py](file:///G:/TradeMindAI/backend/core/database.py)
- Remove `Raw Credential Length` print statements.
- Wrap Firebase initialization in a clean try/except that logs only high-level status (SUCCESS/FAIL) without metadata.

## Verification Plan

### Automated Verification
- **Local Namespace Check:** `celery -A backend.workers.tasks.celery_app inspect registered` should show `backend.workers.tasks.run_shadow_cycle_task`.
- **Local Routing Check:** Verify `celery_app.conf.task_routes` (if added) or decorator-level routing.

### Manual Verification (Cloud Logs)
1.  **Deployment:** Push to Railway and wait for service restarts.
2.  **Worker Log Audit:** Confirm `[queues] .> shadow` appears during startup.
3.  **Beat Log Audit:** Confirm `Scheduler: Sending due task backend.workers.tasks.run_shadow_cycle_task` appears every 30 mins (during IST market hours).
4.  **API Audit:** Verify `/api/v1/shadow/performance` no longer returns 500 errors after idle periods.

## Success Criteria
- [ ] Worker consumes `shadow` queue.
- [ ] Beat dispatches Shadow cycle.
- [ ] Neon connection remains stable (No "SSL closed unexpectedly").
- [ ] **Evaluation Cycles** increments to 11+ in the cloud.
