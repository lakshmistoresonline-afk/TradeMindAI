# PHASE 5H.0: SHADOW ENGINE RAILWAY READINESS AUDIT

## 1. Current Architecture
The Shadow Engine currently operates in a **Local-Primary / Cloud-Mirror** architecture.
- **Engine Execution:** Manual execution on a local PC using PowerShell scripts and Python.
- **Authoritative Database:** Local SQLite (`backend/local_operational.db`).
- **Cloud Visibility:** Consolidated metrics are pushed to Firestore via `ShadowSyncService` for display on the web dashboard.
- **Railway Role:** Currently serves the **Read-Only API** and WebSocket alerts. Heavy background tasks are disabled.

## 2. Shadow Engine Location
- **File Path:** `production/shadow/shadow_service.py`
- **Class:** `ShadowService`
- **Method:** `run_shadow_cycle()`
- **Authoritative DB:** `backend/local_operational.db`

## 3. Shadow Pipeline Trace
| Stage | Source File |
| :--- | :--- |
| **Market Data** | `backend/infrastructure/repositories/yfinance_provider.py` |
| **NIFTY 200 Universe** | `scripts/universe/nifty200_canonical.py` |
| **Strategy v2.2** | `backend/services/signal_engine.py` |
| **Model Runtime** | `backend/ml/registry/` (Champion joblib files) |
| **Signal Generation** | `container.signal_engine.generate_signal()` |
| **shadow_events** | SQL Table (`ShadowEventDB`) |
| **shadow_signals** | SQL Table (`ShadowSignalDB`) |
| **OutcomeEngine** | `backend/services/outcome_engine.py` |
| **Daily Report** | `production/reports/generate_shadow_report.py` |

## 4. Current Execution Status
- **Location:** **LOCAL PC ONLY**.
- **Scheduler:** None in production. `backend/workers/tasks.py` has all schedules commented out for "Railway Safety."
- **Worker:** Celery workers are configured but not running the shadow cycle.
- **Trigger:** Manual launch via `python production/shadow/shadow_service.py`.

## 5. Database Authority Matrix
| Component | Database | Read/Write | Authoritative? |
| :--- | :--- | :--- | :--- |
| **shadow_events** | `backend/local_operational.db` | Write | **YES** |
| **shadow_signals** | `backend/local_operational.db` | Read/Write | **YES** |
| **Outcomes** | `backend/local_operational.db` | Write | **YES** |
| **Reports** | Markdown / JSON | Write | NO (Derived) |
| **Web Dashboard** | Cloud Firestore | Read | NO (Mirror) |

## 6. Railway Configuration Audit
- **Deployment:** Uses `backend/Dockerfile` and `backend/start.sh`.
- **Service Type:** API only (Default).
- **Redis:** Configured in `tasks.py` via `settings.REDIS_URL`.
- **PostgreSQL:** Configured in `postgres.py` via `settings.POSTGRES_URL`.
- **Celery:** Configured but **Disabled**.

## 7. Railway Safety Policy Audit
- **Source:** `docs/RAILWAY_RESOURCE_POLICY.md`.
- **Constraint:** Labels **Signal Generation** and **Signal Audit** as "HEAVY" and "DISABLED" on Railway to minimize credit consumption.
- **Blocker:** Running the 24/7 Shadow Engine on Railway currently violates the established Resource Policy.

## 8. Strategy & Universe Verification
- **Universe:** Strictly **NIFTY 200** (Verified in `shadow_service.py`).
- **Strategy Version:** Strictly **v2.2** (Enforced in `ShadowService.STRATEGY_VERSION` and `SignalEngine`).
- **Freeze Status:** **PASS**. All parameters are hardcoded and non-modifiable via API/UI.

## 9. PC Dependencies (Blockers for Railway)
1. **Local SQLite:** The authoritative state is trapped in a local file.
2. **Model Binaries:** Champion models (~65MB+) must be present in the container image.
3. **Manual Trigger:** Requires a human to run the `.ps1` or `.py` scripts.
4. **Volume:** SQLite database file is not persisted across Railway redeployments unless using a Volume.

## 10. Required Changes for 24/7 Railway Execution
1. **DB Migration:** Move `shadow_signals` and `shadow_events` to a hosted PostgreSQL (e.g., Neon).
2. **Policy Update:** Amend `RAILWAY_RESOURCE_POLICY.md` to permit lightweight "Shadow Monitoring" tasks.
3. **Celery Activation:** Uncomment the `audit-active-signals` and add a new `run-shadow-scan` task in `tasks.py`.
4. **Environment:** Ensure `POSTGRES_URL` and `REDIS_URL` are correctly set in Railway variables.

## 11. Risk Assessment
- **Cost:** Running a full NIFTY 200 scan every 15-30 mins will consume credits.
- **Concurrency:** Using a hosted DB prevents "PC vs Railway" data splits.
- **Reliability:** Railway provides better uptime than a local PC for 24/7 monitoring.

## 12. Recommended Architecture
**API + Celery Worker + Celery Beat**
- **Beat:** Triggers `run_shadow_cycle` every 30 minutes.
- **Worker:** Executes the scan and outcome resolution.
- **API:** Serves the dashboard data from hosted PostgreSQL.

## 13. Exact Files Requiring Modification (Phase 6 Candidate)
- `backend/workers/tasks.py`: Add shadow tasks and uncomment beat schedule.
- `docs/RAILWAY_RESOURCE_POLICY.md`: Update permission for shadow monitoring.
- `backend/core/config.py`: Finalize `POSTGRES_URL` priority.

## Final Status
`RAILWAY_SHADOW_READY_WITH_CHANGES`

> [!NOTE]
> The engine is technically capable of running on Railway today, but is intentionally held local by the **Resource Policy** and the **SQLite dependency**. Migration to hosted PostgreSQL is the critical path.
