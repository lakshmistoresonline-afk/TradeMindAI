# TradeMind AI - Step 4.5.2 Shadow Intraday Runner
Write-Host "============================================================" -ForegroundColor White
Write-Host " TRADEMIND AI - SHADOW INTRADAY (MARKET AWARE)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor White

$python = ".venv\Scripts\python.exe"

# 1. Session Check
Write-Host "[*] Validating Market Session..." -ForegroundColor Gray
$session = & $python -c "from backend.services.market_calendar import IndianMarketCalendar; print(IndianMarketCalendar.get_current_session())"
Write-Host "Current Session: $session"

if ($session -ne "OPEN") {
    Write-Host "[!] Market is NOT OPEN. Session: $session. Exiting cleanly." -ForegroundColor Yellow
    exit 0
}

# 2. Run Engine
Write-Host "[*] Executing Intraday Shadow Cycle..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_shadow_engine.py --mode intraday
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Shadow engine failed." -ForegroundColor Red; exit 1 }

# 3. Sync Firebase
Write-Host "[*] Synchronizing to Cloud..." -ForegroundColor Gray
& $python scripts/accuracy/step4_5_firebase_sync.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Sync failed." -ForegroundColor Red; exit 1 }

Write-Host "[SUCCESS] Intraday Cycle Complete." -ForegroundColor Green
