# Railway Resource & Cost Management Policy (P0)

**Status**: STRICT ENFORCEMENT

## 1. Objective
To maintain 100% operational uptime while minimizing credit consumption on Railway by moving all heavy background computation and automated tasks to local manual workflows.

## 2. Process Classification

| Process | Category | Environment | Railway Status | Local Equivalent |
| :--- | :--- | :--- | :--- | :--- |
| **Lightweight API** | Necessary | Railway | **ENABLED** | N/A |
| **Real-time SSE** | Necessary | Railway | **ENABLED** | N/A |
| **Full Universe Sync** | **HEAVY** | **LOCAL** | **DISABLED** | `./scripts/windows/01_sync_market.ps1` |
| **Market Intel (Regime)**| **HEAVY** | **LOCAL** | **DISABLED** | `./scripts/windows/02_process_intelligence.ps1` |
| **Signal Audit** | **HEAVY** | **LOCAL** | **DISABLED** | `./scripts/windows/02_process_intelligence.ps1` |
| **ML Training** | **HEAVY** | **LOCAL** | **DISABLED** | `./scripts/windows/03_train_models.ps1` |
| **Backtesting** | **HEAVY** | **LOCAL** | **DISABLED** | `./scripts/windows/04_run_validation.ps1` |
| **Shadow Monitoring**| Lightweight| Railway | **ENABLED** | `production/shadow/shadow_service.py` |
| **Signal Generation** | **HEAVY** | **LOCAL** | **DISABLED** | `./scripts/windows/05_generate_signals.ps1` |

## 3. Mandatory Rules
1. **ZERO WORKER POLICY (EXCEPT SHADOW)**: Celery workers/Beat are permitted ONLY for certified Shadow Monitoring (Strategy v2.2).
2. **NO API SIDE-EFFECTS**: API endpoints that initiate heavy tasks are disabled.
3. **MANUAL FIRST**: All database updates, model retraining, and non-shadow signal generation MUST be initiated manually from a local machine using provided scripts.
4. **CREDIT PROTECTION**: Bulk synchronization of NIFTY 200 or F&O data on Railway is strictly prohibited.

## 4. Local Windows Workflow

Execute these scripts from the project root using `powershell.exe`.

| Script | Purpose |
| :--- | :--- |
| `00_check_environment.ps1` | Environment & Dependency Audit |
| `01_sync_market.ps1` | NIFTY 200 & F&O Master Sync |
| `02_process_intelligence.ps1` | Regime Detection & Scanner |
| `03_train_models.ps1` | Local ML Model Training |
| `04_run_validation.ps1` | Walk-Forward Backtesting |
| `05_generate_signals.ps1` | Bulk Production Signals |

---

## 5. Shadow Engine on Railway
The certified Strategy v2.2 Shadow Engine is permitted to run on Railway under the following constraints:
- **Interval**: Maximum once every 30 minutes.
- **Queue**: Strictly routed to the `shadow` queue.
- **Concurrency**: `concurrency=1` to minimize CPU burst.

## 5. Failure Protocol
If a required model or dataset is missing on Railway, the API will return:
- `status: MODEL_NOT_READY`
- `status: DATA_UNAVAILABLE`

**DO NOT** attempt to trigger these processes via API calls. Run the corresponding local script first.
