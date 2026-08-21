# TradeMind AI - Step 4.4.1 Full NIFTY 200 Walk-Forward Runner
Write-Host "--- STEP 4.4.1 FULL NIFTY 200 WALK-FORWARD START ---" -ForegroundColor Cyan

$python = ".venv\Scripts\python.exe"

# 1. Baseline Manifest
Write-Host "[*] Phase 1: Baseline Integrity..." -ForegroundColor Gray
& $python -c "import hashlib, json; h = hashlib.sha256(open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json','rb').read()).hexdigest(); print(f'SHA256: {h}')"

# 2. Reconcile existing Step 4.4
Write-Host "[*] Phase 2: Report Reconciliation..." -ForegroundColor Gray
# (Manual report already created in Phase 3 of plan)

# 3. Full NIFTY 200 Retraining
Write-Host "[*] Phase 3: Full NIFTY 200 Retraining (Approx 30-60 mins)..." -ForegroundColor Gray
& $python scripts/accuracy/step4_4_walk_forward.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Walk-forward engine failed." -ForegroundColor Red; exit $LASTEXITCODE }

# 4. Portfolio Simulation
Write-Host "[*] Phase 4: Portfolio Simulation..." -ForegroundColor Gray
& $python scripts/accuracy/walk_forward_portfolio.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Portfolio simulation failed." -ForegroundColor Red; exit $LASTEXITCODE }

# 5. Audits & Robustness
Write-Host "[*] Phase 5: Audits & Robustness Analysis..." -ForegroundColor Gray
& $python scripts/accuracy/step4_4_1_auditor.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Audit suite failed." -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "--- STEP 4.4.1 VALIDATION COMPLETE ---" -ForegroundColor Green
Write-Host "Status: STEP4.4_FULL_NIFTY200_WALK_FORWARD_VALIDATED"
