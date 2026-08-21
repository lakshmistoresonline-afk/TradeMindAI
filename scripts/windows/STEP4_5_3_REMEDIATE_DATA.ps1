# TradeMind AI - Step 4.5.3 NIFTY 200 Data & Feature Remediation Runner
Write-Host "============================================================" -ForegroundColor White
Write-Host " TRADEMIND AI - STEP 4.5.3 DATA PIPELINE REMEDIATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor White

$python = ".venv\Scripts\python.exe"

# 1. Environment Check
Write-Host "[1] Checking Environment..." -ForegroundColor Gray
if (!(Test-Path $python)) { Write-Host "[FAIL] Virtual environment not found." -ForegroundColor Red; exit 1 }

# 2. Run Remediation Script (Backfill + Features)
Write-Host "[2] Remediating problematic symbols (GUJGASLTD, LTIM, PEL, TATAMOTORS)..." -ForegroundColor Gray
& $python scripts/accuracy/remediate_data.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Remediation script failed." -ForegroundColor Red; exit 1 }

# 3. Train Models for remediated symbols
Write-Host "[3] Training champion models for remediated symbols..." -ForegroundColor Gray
& $python scripts/accuracy/train_problematic.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Training failed." -ForegroundColor Red; exit 1 }

# 4. Run Regression Tests
Write-Host "[4] Running NIFTY 200 Data Quality Regression Tests..." -ForegroundColor Gray
& $python tests/test_nifty200_data_quality.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Regression tests failed." -ForegroundColor Red; exit 1 }

# 5. Run full Shadow Scan for final state
Write-Host "[5] Running full NIFTY 200 Shadow Diagnostic Scan..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_shadow_engine.py --mode eod
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Shadow engine failed." -ForegroundColor Red; exit 1 }

# 6. Sync to Cloud
Write-Host "[6] Synchronizing remediated status to Firebase..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_firebase_sync.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Firebase sync failed." -ForegroundColor Red; exit 1 }

Write-Host "============================================================" -ForegroundColor White
Write-Host " DATA REMEDIATION COMPLETE. STATUS: STEP4.5.3_DATA_REMEDIATION_COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor White
