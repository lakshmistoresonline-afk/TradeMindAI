# TradeMind AI - Step 4.3 Robustness Validation Runner
Write-Host "--- STEP 4.3 ROBUSTNESS VALIDATION START ---" -ForegroundColor Cyan

$python = ".venv\Scripts\python.exe"

Write-Host "[*] Phase 1: Sector Population..."
& $python scripts/accuracy/populate_sectors.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Sector population failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[*] Phase 2: Core Validation & Remediation..."
& $python scripts/accuracy/step4_3_1_remediation.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Remediation audit failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[*] Phase 3: Regime Analysis..."
& $python scripts/accuracy/step4_3_1_regime.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Regime audit failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[*] Phase 4: Liquidity Audit..."
& $python scripts/accuracy/step4_3_1_liquidity.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Liquidity audit failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[*] Phase 5: Statistical & Drift Audit..."
& $python scripts/accuracy/step4_3_1_statistical.py
& $python scripts/accuracy/step4_3_1_drift.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Statistical/Drift audit failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[*] Phase 6: Generating Final Reports..."
& $python scripts/accuracy/step4_3_1_finalizer.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Finalization failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "--- STEP 4.3 VALIDATION COMPLETE ---" -ForegroundColor Green
Write-Host "Status: STEP4.3_VALIDATION_REMEDIATION_COMPLETE"
