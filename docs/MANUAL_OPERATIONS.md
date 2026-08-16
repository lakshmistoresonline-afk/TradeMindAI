# TradeMind AI Manual Operations Guide

This document outlines the required manual steps for maintaining the TradeMind AI quantitative engine.

## 1. Environment Readiness

Before any operation, ensure your local environment is calibrated:
```powershell
./scripts/windows/00_check_environment.ps1
```

## 2. Daily Market Synchronization

Run the synchronization script to update NIFTY 200 constituents, F&O instruments, and historical candles:
```powershell
./scripts/windows/01_sync_market.ps1
```

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
```powershell
./scripts/windows/02_process_intelligence.ps1
```

## 4. Periodic ML Retraining

To update champion models with recent price action:
```powershell
./scripts/windows/03_train_models.ps1
```

## 5. Quantitative Validation

Run the walk-forward validation pipeline to audit engine accuracy:
```powershell
./scripts/windows/04_run_validation.ps1
```

## 6. Signal Generation

Generate and upload fresh production signals:
```powershell
./scripts/windows/05_generate_signals.ps1
```

## 7. Data Forensic Cleanup

To remove synthetic or corrupt derivation data:
```bash
python -m scripts.maintenance.data_cleanup --confirm --no-dry-run
```
