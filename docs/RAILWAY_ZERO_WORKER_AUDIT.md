# Railway Zero-Worker Audit & Deactivation Report

## 1. Executive Summary
To resolve production errors (`ModuleNotFoundError: No module named 'production'`) and ensure high availability of the core API, all autonomous background execution on Railway has been deactivated. The TradeMind AI architecture has transitioned to a **Cloud-Web / Local-Compute** hybrid model.

## 2. Changes Implemented

### A. Railway Startup Hardening (`backend/start.sh`)
- **Strict Role Enforcement**: The startup script now explicitly allows only the `api` role.
- **Fail-Closed Logic**: Any attempt to start a `worker`, `beat`, `shadow-worker`, or `shadow-beat` on Railway will now result in an immediate exit with a critical error message.
- **Unified Entry Point**: All services pointing to this repo will now either start the API or fail, preventing unauthorized background processing.

### B. Schedule Deactivation (`backend/workers/tasks.py`)
- **Conditional Beat Schedule**: The Celery `beat_schedule` is now dynamically emptied if `ENVIRONMENT=production` is detected.
- **Namespace Protection**: Prevents any task from being triggered by a scheduler even if one were to be accidentally started.

### C. Resource Protection
- **Railway Workers**: 0
- **Railway Schedulers**: 0
- **Railway Shadow Scanning**: 0 (Moved to Local)

## 3. Local Replacement Workflows
All background tasks must now be executed manually from a local Windows environment using the established scripts.

| Previous Automated Task | Local Manual Replacement |
| :--- | :--- |
| **Market Data Sync** | `.\scripts\windows\01_sync_market.ps1` |
| **Shadow Monitoring** | `.\.venv\Scripts\python.exe production/shadow/shadow_service.py` |
| **Outcome Resolution** | `.\.venv\Scripts\python.exe scripts/maintenance/audit_open_signals.py` |
| **ML Training** | `.\scripts\windows\03_train_models.ps1` |
| **Signal Generation** | `.\scripts\windows\05_generate_signals.ps1` |

## 4. Final Architecture
- **Railway**: Hosts the FastAPI API and provides the Web Shadow Monitor interface. Strictly read-only for market data processing.
- **Neon PostgreSQL**: Authoritative production database, updated by local manual workflows.
- **Local PC**: Primary execution engine for all heavy processing, strategy scanning, and evidence accumulation.

## 5. Status Matrix
| Parameter | Value |
| :--- | :--- |
| **Railway Workers** | **0 (DEACTIVATED)** |
| **Railway Schedulers** | **0 (DEACTIVATED)** |
| **Cloud-Web Status** | **ACTIVE** |
| **Production Risk** | **MINIMIZED** |

---
**Verdict**: The system is now hardened against unauthorized cloud execution. All `production` module dependencies are isolated to the local environment.
