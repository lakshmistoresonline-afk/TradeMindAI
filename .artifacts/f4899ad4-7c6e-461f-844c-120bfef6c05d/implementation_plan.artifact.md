# Implementation Plan - Phase 6.4: Celery Routing & Data Provider Remediation

This phase resolves the infrastructure defects identified in the Phase 6.4 forensic audit, enabling autonomous PC-independent Shadow execution on Railway.

## User Review Required

> [!IMPORTANT]
> **TASK NAMESPACE ALIGNMENT:** We are standardizing the Celery task namespace to `backend.workers.tasks` to ensure the Beat scheduler and Worker remain synchronized.
>
> **QUEUE ROUTING:** Every production Shadow task (including heartbeats) will be explicitly routed to the `shadow` queue to prevent delivery to generic workers.
>
> **DATA PROVIDER FIX:** We will update the NIFTY symbol mapping to resolve the 404/Delisted errors seen in the logs.

## Proposed Changes

### 1. Celery Routing Hardening
#### [MODIFY] [tasks.py](file:///G:/TradeMindAI/backend/workers/tasks.py)
- Change `celery_app = Celery("tasks", ...)` to `celery_app = Celery("backend.workers.tasks", ...)`.
- Add `queue="shadow"` to the `@celery_app.task` decorator for `terminal_heartbeat`.
- Ensure all automated tasks in `beat_schedule` use the consistent namespace.

### 2. Market Data Resiliency
#### [MODIFY] [yfinance_provider.py](file:///G:/TradeMindAI/backend/infrastructure/repositories/yfinance_provider.py)
- Update `_map_symbol` for NIFTY to use the currently active 2026 Yahoo Finance ticker.
- Implement more robust error handling for heartbeat price discovery.

### 3. Monitoring API Alignment
#### [MODIFY] [shadow.py](file:///G:/TradeMindAI/backend/api/v1/endpoints/shadow.py)
- Update heartbeat lookup query to use the new standardized task namespace.

## Verification Plan

### Automated Verification
- **Task Registration Test:** Run `celery -A backend.workers.tasks.celery_app inspect registered` locally and verify tasks appear as `backend.workers.tasks.*`.
- **Routing Verification:** Verify via Redis (if possible) that heartbeat tasks are arriving in the `shadow` queue.

### Manual Acceptance Test
1. **Redeploy to Railway:** Apply changes and monitor logs.
2. **Delivery Audit:** Confirm "Received task: backend.workers.tasks.run_shadow_cycle_task" appears in the Shadow Worker logs.
3. **Dashboard Update:** Confirm **Evaluation Cycles** increment autonomously without local intervention.

## Final Status Matrix
| Milestone | Expected | Status |
| :--- | :--- | :--- |
| Task Name Match | Synchronized | `PENDING` |
| Queue Delivery | Target: `shadow` | `PENDING` |
| NIFTY LTP | Valid Number | `PENDING` |
| **PC Independent**| YES | `PENDING` |
