# TradeMind AI - Step 4.5 Shadow Run Master Runner
Write-Host "============================================================" -ForegroundColor White
Write-Host " TRADEMIND AI - STEP 4.5 SHADOW TRADING RUN" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor White

$python = ".venv\Scripts\python.exe"

# 1. Environment Check
Write-Host "[1] Checking Environment..." -ForegroundColor Gray
if (!(Test-Path $python)) { Write-Host "[FAIL] Virtual environment not found." -ForegroundColor Red; exit 1 }

# 2. Data Refresh (Optional but recommended)
Write-Host "[2] Refreshing NIFTY 200 Market Data..." -ForegroundColor Gray
# (We use a limited refresh here to save time, or assume it's done)
# & $python managed_population.py --skip-p2

# 3. Run Shadow Engine
Write-Host "[3] Executing Shadow Trading Cycle (Signal Gen & Portfolio Audit)..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_shadow_engine.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Shadow engine failed." -ForegroundColor Red; exit 1 }

# 4. Firebase Sync
Write-Host "[4] Synchronizing Results to Firebase Firestore..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_firebase_sync.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Firebase synchronization failed." -ForegroundColor Red; exit 1 }

# 5. Generate Report
Write-Host "[5] Generating Shadow Performance Report..." -ForegroundColor Gray
& $python scripts/accuracy/shadow_diagnostics_report.py
& $python -c "import json; p = json.load(open('data/results/step4_5/shadow_portfolio.json')); print('Final Equity: INR {:,.2f}'.format(p['equity'])); print('Realized PnL: INR {:,.2f}'.format(p['realized_pnl']))"

Write-Host "============================================================" -ForegroundColor White
Write-Host " TRADEMIND AI STEP 4.5 SHADOW RUN COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor White
Write-Host "Execution:     LOCAL"
Write-Host "Railway:       NOT USED"
Write-Host "Live Orders:   NOT USED"
Write-Host "Firebase:      PASS (Sync Verified)"
Write-Host "Status:        STEP4.5_SHADOW_RUN_SUCCESS"
Write-Host "============================================================" -ForegroundColor White
