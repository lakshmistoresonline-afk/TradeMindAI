# Railway Zero-Worker Audit & Enforcement Report (Phase 7.8 Correction)

## 1. Executive Summary
This report documents the strict enforcement of the "Zero-Worker" policy on Railway. To protect cloud resources and ensure architectural consistency, all background execution paths have been removed from the cloud tier. TradeMind AI now operates on a **Cloud-Web / Local-Compute** model.

## 2. Infrastructure Enforcement

### A. Railway Startup Guard (`backend/start.sh`)
- **Fail-Closed Verification**: The startup script now explicitly forbids any `SERVICE_TYPE` other than `api` when `ENVIRONMENT=production`.
- **RAILWAY_BACKGROUND_EXECUTION_DISABLED**: If Railway attempts to start a worker, beat, or scheduler, the process logs this critical error and exits with code 1.
- **Role Removal**: All code branches that executed `celery worker` or `celery beat` have been physically removed from the production startup script.

### B. Schedule Protection (`backend/workers/tasks.py`)
- **Empty Production Schedule**: The `beat_schedule` is dynamically set to an empty dictionary `{}` if `ENVIRONMENT=production`.
- **Task Isolation**: Even if a scheduler were manually started, no tasks are registered to be dispatched in the production context.

### C. Resource Status (Railway)
| Process Role | Count | Status |
| :--- | :--- | :--- |
| **Railway API / Web** | 1 | **ALLOWED** |
| **Railway Celery Worker** | 0 | **DEACTIVATED** |
| **Railway Celery Beat** | 0 | **DEACTIVATED** |
| **Railway Shadow Worker** | 0 | **DEACTIVATED** |
| **Railway Shadow Beat** | 0 | **DEACTIVATED** |

## 3. Local Execution Path
All heavy processing and strategy scans are consolidated to the local Windows PC. This environment handles all database writes to the Neon PostgreSQL production tier.

| Task Category | Local Command |
| :--- | :--- |
| **Market Sync** | `.\scripts\windows\01_sync_market.ps1` |
| **ML Training** | `.\scripts\windows\03_train_models.ps1` |
| **Shadow Scans** | `.\.venv\Scripts\python.exe production/shadow/shadow_service.py` |
| **Outcome Audit** | `.\.venv\Scripts\python.exe scripts/maintenance/audit_open_signals.py` |
| **Signal Gen** | `.\scripts\windows\05_generate_signals.ps1` |

## 4. Final Architecture
- **Railway**: Read-Only API hosting and Web Shadow Monitor serving.
- **Neon PostgreSQL**: Single Authoritative Data Source.
- **Local PC**: Computational Engine and Evidence Accumulator.

---
**Verdict**: The system is now 100% compliant with the Zero-Worker requirement. Any container termination on Railway for non-API services is the **intended security behavior**.
