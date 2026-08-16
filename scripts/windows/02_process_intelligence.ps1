<<<<<<< HEAD
# TradeMind AI Market Intelligence Processing
# Step 2: Market Intelligence

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [2/6] MARKET INTELLIGENCE PROCESSING"
Write-Host "============================================================"

# Activate venv
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 1. Run Intelligence Engine
Write-Host "[*] Processing Market Intelligence (Regime + Reports)..."
python -m scripts.market_intelligence.process_intelligence
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Intelligence processing failed."
    exit 1
}

# 2. Run Opportunity Scanner
Write-Host "[*] Running NIFTY 200 Opportunity Scanner..."
python -m scripts.signals.refresh_rankings
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Opportunity scanning failed."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] INTELLIGENCE PROCESSED"
=======
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
>>>>>>> origin/main
Write-Host "============================================================"
exit 0
