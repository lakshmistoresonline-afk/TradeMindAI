# Railway Resource & Cost Management Policy (P0)

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
| **Signal Generation** | **HEAVY** | **LOCAL** | **DISABLED** | `./scripts/windows/05_generate_signals.ps1` |

## 3. Mandatory Rules
1. **NO AUTOMATED WORKERS**: Celery Beat schedule has been cleared. No background tasks will trigger automatically on Railway.
2. **NO API SIDE-EFFECTS**: API endpoints (like `/trigger`) that previously initiated heavy tasks are now disabled or return a manual instruction status.
3. **MANUAL FIRST**: All database updates, model retraining, and signal generation MUST be initiated manually from a local machine.
4. **CREDIT PROTECTION**: Automated NIFTY 100/200 processing is strictly prohibited on Railway infrastructure.

## 4. Operational Transition
To update the production database with fresh signals or data, follow the **[MANUAL_OPERATIONS.md](file:///D:/TradeMindAI/docs/MANUAL_OPERATIONS.md)** guide.
