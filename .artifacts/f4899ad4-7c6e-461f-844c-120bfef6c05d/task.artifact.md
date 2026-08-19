# Task Checklist - Phase 7.7: Fix Railway Beat Service Role

- `[/]` Infrastructure Hardening
    - `[ ]` Enhance `backend/start.sh` with explicit role logging
    - `[ ]` Add schedule count logging to `backend/workers/tasks.py`
- `[ ]` Configuration Correction (Railway)
    - `[ ]` Update `trademind-beat` SERVICE_TYPE to `shadow-beat`
- `[ ]` Verification
    - `[ ]` Confirm "Shadow Celery Beat" starting message in logs
    - `[ ]` Verify task dispatch in Beat logs
    - `[ ]` Verify task receipt in Worker logs
    - `[ ]` Update `daily_shadow_report.md` with cloud-cycle success
