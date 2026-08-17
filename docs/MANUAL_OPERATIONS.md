# TradeMind AI — Manual Local Operations (P0)

## 1. Overview
As part of the Railway Safety & Cost Management policy, all heavy background computation (Data Sync, ML, Backtesting) must be executed manually from a local Windows machine. Railway is reserved for the lightweight API and live inference only.

## 2. Windows Manual Workflow (PowerShell)

Execute these scripts from the project root using `powershell.exe`.

### **STEP 0: Environment Verification**
Ensures all Python dependencies and database connections are ready for local processing.
```powershell
./scripts/windows/00_check_environment.ps1
```

### **STEP 1: Market Data Synchronization**
Synchronizes the Nifty 200 universe, fetches fresh candles, and cleans obsolete data.
```powershell
./scripts/windows/01_sync_market.ps1
```

#### 1.1 Manual Historical Backfill (Optional/Resume)
If you need to resume a failed historical sync or perform a deep backfill:
```powershell
./scripts/windows/01B_sync_historical.ps1
```
This script supports resumable processing via `backend/data/sync_checkpoint.json`.

#### 1.2 Historical Validation Gate
To strictly verify the current state of historical data:
```powershell
./scripts/windows/01B_validate_historical.ps1
```
This gate must pass (exit 0) before any AI analysis stages can be executed.
Detailed coverage report is available at `docs/NIFTY200_HISTORICAL_COVERAGE_REPORT.md`.

### **STEP 2: Market Intelligence Processing**
Processes market intelligence (Regime detection) and audits active signal outcomes.
```powershell
./scripts/windows/02_process_intelligence.ps1
```

### **STEP 3: Model Training & Calibration**
Rebuilds feature store, trains champion models locally, and performs probability calibration.
```powershell
./scripts/windows/03_train_models.ps1
```

### **STEP 4: Backtesting & Validation**
Runs walk-forward validation and generates performance reports.
```powershell
./scripts/windows/04_run_validation.ps1
```

### **STEP 5: Signal Generation**
Generates fresh live signals for Equity, Futures, and Options segments based on the latest models.
```powershell
./scripts/windows/05_generate_signals.ps1
```

---

## 3. Command Reference Table

| Operation | Command | Execution Environment |
| :--- | :--- | :--- |
| **Sync NIFTY 200** | `python terminal_master_scripts/02_populate_stocks_master.py` | Local |
| **Sync F&O Contracts** | `python terminal_master_scripts/03_seed_derivative_instruments.py` | Local |
| **Audit Signal Outcomes**| `python scripts/maintenance/audit_production_engine.py` | Local |
| **Data Cleanup** | `python scripts/maintenance/data_cleanup.py --no-dry-run --confirm` | Local |
| **Market Regime Detection**| `python -m scripts.market_intelligence.detect` | Local |

---

## 4. Railway Worker Audit

| Worker / Task | Purposed | Railway Status | Local Equivalent |
| :--- | :--- | :--- | :--- |
| `analyze_nifty_100` | Full Universe Sync | **DISABLED** | `01_sync_market.ps1` |
| `process_market_intel`| Regime Detection | **DISABLED** | `02_process_intelligence.ps1` |
| `audit_signals_task` | Outcome Resolution | **DISABLED** | `scripts/maintenance/audit_production_engine.py`|
| `terminal-heartbeat` | API Health Check | Lightweight Only | N/A |

---

## 5. Failure Protocol
If a required model or dataset is missing on Railway, the API will return:
- `status: MODEL_NOT_READY`
- `status: DATA_UNAVAILABLE`

**DO NOT** attempt to trigger these processes via API calls. Run the corresponding local script first.
