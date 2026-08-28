# TradeMind AI - Step 4.5.2 Shadow EOD Runner
Write-Host "============================================================" -ForegroundColor White
Write-Host " TRADEMIND AI - SHADOW EOD RECONCILIATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor White

$python = ".venv\Scripts\python.exe"

# 1. Run Engine in EOD mode (Force reconciliation)
Write-Host "[*] Executing EOD Shadow Cycle..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_shadow_engine.py --mode eod
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Shadow engine failed." -ForegroundColor Red; exit 1 }

# 2. Sync Firebase
Write-Host "[*] Synchronizing to Cloud..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_firebase_sync.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Sync failed." -ForegroundColor Red; exit 1 }

# 3. Generate Diagnostics Report
Write-Host "[*] Generating Diagnostic Summary..." -ForegroundColor Gray
& $python scripts/accuracy/shadow_diagnostics_report.py

# 4. Final Verification
Write-Host "[*] Verifying Cloud Visibility..." -ForegroundColor Gray
& $python scripts/accuracy/verify_firebase_shadow.py

Write-Host "============================================================" -ForegroundColor White
Write-Host " SHADOW EOD COMPLETE. STATUS: STEP4.5.2_SHADOW_RUN_SUCCESS" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor White
