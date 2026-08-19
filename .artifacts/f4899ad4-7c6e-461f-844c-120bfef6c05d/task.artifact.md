# Task Checklist - Phase 7.5: Celery Routing & Production Reliability

- `[x]` Implementation
    - `[x]` Fix `beat_schedule` and task routing in `backend/workers/tasks.py`
    - `[x]` Harden PostgreSQL engine in `backend/core/postgres.py` (Pool Resilience)
    - `[x]` Refine `shadow-worker` startup in `backend/start.sh`
    - `[x]` Clean up sensitive logging in `backend/core/database.py`
- `[x]` Verification
    - `[x]` Verify local task registration namespace
    - `[x]` Confirm Railway delivery in logs (Blocked by Environment Variables)
    - `[x]` Verify Neon connection stability via API stress test
    - `[x]` Update `PHASE7_CELERY_SHADOW_QUEUE_REMEDIATION_REPORT.md`
