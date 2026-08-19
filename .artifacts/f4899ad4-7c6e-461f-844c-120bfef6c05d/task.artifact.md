# Task Checklist - Phase 7.5: Celery Routing & Production Reliability

- `[/]` Implementation
    - `[ ]` Fix `beat_schedule` and task routing in `backend/workers/tasks.py`
    - `[ ]` Harden PostgreSQL engine in `backend/core/postgres.py` (Pool Resilience)
    - `[ ]` Refine `shadow-worker` startup in `backend/start.sh`
    - `[ ]` Clean up sensitive logging in `backend/core/database.py`
- `[ ]` Verification
    - `[ ]` Verify local task registration namespace
    - `[ ]` Confirm Railway delivery in logs (Target: `shadow` queue)
    - `[ ]` Verify Neon connection stability via API stress test
    - `[ ]` Update `PHASE7_CELERY_SHADOW_QUEUE_REMEDIATION_REPORT.md`
