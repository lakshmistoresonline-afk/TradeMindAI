# Railway Resource Usage Policy

**Status**: STRICT ENFORCEMENT

## 1. Zero Worker Policy

TradeMind AI explicitly prohibits the execution of heavy background processing on Railway. This includes, but is not limited to:

- **Celery Workers**: Not permitted on Railway.
- **Celery Beat**: Not permitted on Railway.
- **Scheduled Jobs (Cron)**: No heavy jobs permitted.
- **Market Data Processing**: Bulk synchronization of NIFTY 200 or F&O data is strictly local.
- **ML Training**: Model training, calibration, and walk-forward validation are strictly local.

## 2. Permitted Railway Roles

Railway is reserved for lightweight application serving only:

- **FastAPI Web Server**: API serving and request handling.
- **Authentication**: JWT validation and user management.
- **Real-time Inference**: Single-stock prediction with existing champion models.
- **Database Proxy**: Access to Postgres (Neon) for lightweight reads/writes.
- **Health Heartbeat**: Lightweight status checks only.

## 3. Local Windows Workflow

All P0/P1 heavy operations must be executed manually on the local Windows machine using the provided PowerShell scripts in `scripts/windows/`.

| Script | Purpose |
| :--- | :--- |
| `00_check_environment.ps1` | Environment & Dependency Audit |
| `01_sync_market.ps1` | NIFTY 200 & F&O Master Sync |
| `02_process_intelligence.ps1` | Regime Detection & Scanner |
| `03_train_models.ps1` | Local ML Model Training |
| `04_run_validation.ps1` | Walk-Forward Backtesting |
| `05_generate_signals.ps1` | Bulk Production Signals |
