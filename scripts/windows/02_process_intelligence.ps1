# TradeMind AI - Quantitative Engine Heartbeat (P0)
$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host " TRADEMIND AI - STEP 2: QUANTITATIVE ENGINE HEARTBEAT"
Write-Host "============================================================"

# [1/2] Market Regime Detection
Write-Host "`n[1/2] Detecting Market Regime (Forensic Trend/Vol Analysis)..." -ForegroundColor Cyan
& $PythonExe scripts/market_intelligence/detect.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Market regime detection failed." -ForegroundColor Red
    exit 1
}

# [2/2] Signal Outcome Audit
Write-Host "`n[2/2] Auditing Active Signal Outcomes (Real Data Comparison)..." -ForegroundColor Cyan
& $PythonExe scripts/maintenance/audit_production_engine.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Signal outcome audit failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n============================================================"
Write-Host " [SUCCESS] QUANTITATIVE HEARTBEAT COMPLETE"
Write-Host "============================================================"
exit 0
