# TradeMind AI - Step 4.4 Walk-Forward Validation Runner
Write-Host "--- STEP 4.4 TRUE WALK-FORWARD START ---" -ForegroundColor Cyan

$python = ".venv\Scripts\python.exe"

Write-Host "[*] Executing Walk-Forward Engine (Sample 20 Symbols)..." -ForegroundColor Gray
& $python scripts/accuracy/step4_4_walk_forward.py --limit 20
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Walk-forward engine failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[*] Executing Portfolio Simulation on WF Results..." -ForegroundColor Gray
& $python scripts/accuracy/walk_forward_portfolio.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Portfolio simulation failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "[*] Generating Final Reports..." -ForegroundColor Gray
& $python scripts/accuracy/step4_4_report_gen.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Report generation failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "--- STEP 4.4 VALIDATION COMPLETE ---" -ForegroundColor Green
Write-Host "Status: STEP4.4_WALK_FORWARD_VALIDATED"
