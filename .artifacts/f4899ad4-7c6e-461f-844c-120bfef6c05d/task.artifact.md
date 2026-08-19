# Task Checklist - Phase 6.4: Celery Routing & Data Provider Remediation

- `[/]` Implementation
    - `[ ]` Align Celery namespace in `backend/workers/tasks.py`
    - `[ ]` Route all heartbeat/shadow tasks to `shadow` queue
    - `[ ]` Update NIFTY symbol mapping in `yfinance_provider.py`
- `[ ]` Verification
    - `[ ]` Verify task registration namespace
    - `[ ]` Confirm Railway delivery in logs
    - `[ ]` Update `daily_shadow_report.md` with successful cloud cycle
