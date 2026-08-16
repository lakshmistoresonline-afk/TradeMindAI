<<<<<<< HEAD
# TradeMind AI Manual Operations Guide

This document outlines the required manual steps for maintaining the TradeMind AI quantitative engine.

## 1. Environment Readiness

Before any operation, ensure your local environment is calibrated:
=======
# TradeMind AI — Manual Local Operations (P0)

## 1. Overview
As part of the Railway Safety & Cost Management policy, all heavy background computation (Data Sync, ML, Backtesting) must be executed manually from a local Windows machine. Railway is reserved for the lightweight API and live inference only.

## 2. Windows Manual Workflow (PowerShell)

Execute these scripts from the project root using `powershell.exe`.

### **STEP 0: Environment Verification**
Ensures all Python dependencies and database connections are ready for local processing.
>>>>>>> origin/main
```powershell
./scripts/windows/00_check_environment.ps1
```

<<<<<<< HEAD
## 2. Daily Market Synchronization

Run the synchronization script to update NIFTY 200 constituents, F&O instruments, and historical candles:
=======
### **STEP 1: Market Data Synchronization**
Synchronizes the Nifty 200 universe, fetches fresh candles, and cleans obsolete data.
>>>>>>> origin/main
```powershell
./scripts/windows/01_sync_market.ps1
```

<<<<<<< HEAD
### 2.1 Manual Historical Backfill (Optional/Resume)

If you need to resume a failed historical sync or perform a deep backfill:
```powershell
./scripts/windows/01B_sync_historical.ps1
```
This script supports resumable processing via `backend/data/sync_checkpoint.json`.

### 2.2 Historical Validation Gate

To strictly verify the current state of historical data:
```powershell
./scripts/windows/01B_validate_historical.ps1
```
This gate must pass (exit 0) before any AI analysis stages can be executed.
Detailed coverage report is available at `docs/NIFTY200_HISTORICAL_COVERAGE_REPORT.md`.

## 3. Market Intelligence

Detect the current market regime and refresh opportunity rankings:
=======
### **STEP 2: Quantitative Engine Heartbeat**
Processes market intelligence (Regime detection) and audits active signal outcomes.
>>>>>>> origin/main
```powershell
./scripts/windows/02_process_intelligence.ps1
```

<<<<<<< HEAD
## 4. Periodic ML Retraining

To update champion models with recent price action:
=======
### **STEP 3: Model Training & Calibration**
Rebuilds feature store, trains champion models locally, and performs probability calibration.
>>>>>>> origin/main
```powershell
./scripts/windows/03_train_models.ps1
```

<<<<<<< HEAD
## 5. Quantitative Validation

Run the walk-forward validation pipeline to audit engine accuracy:
=======
### **STEP 4: Backtesting & Validation**
Runs walk-forward validation and generates performance reports.
>>>>>>> origin/main
```powershell
./scripts/windows/04_run_validation.ps1
```

<<<<<<< HEAD
## 6. Signal Generation

Generate and upload fresh production signals:
=======
### **STEP 5: Signal Generation**
Generates fresh live signals for Equity, Futures, and Options segments based on the latest models.
>>>>>>> origin/main
```powershell
./scripts/windows/05_generate_signals.ps1
```

<<<<<<< HEAD
## 7. Data Forensic Cleanup

To remove synthetic or corrupt derivation data:
```bash
python -m scripts.maintenance.data_cleanup --confirm --no-dry-run
```
=======
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
>>>>>>> origin/main
