# TradeMind AI Market Intelligence Processing (Consolidated v2.2)
$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [2/6] MARKET INTELLIGENCE PROCESSING"
Write-Host "============================================================"

# 1. Environment Validation
& scripts/windows/00_check_environment.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

# Activate venv
$VENV_PATH = "$(Get-Location)/.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 2. Run Intelligence Engine
Write-Host "[*] Processing Market Intelligence (Regime Detection)..."
python scripts/market_intelligence/detect.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Intelligence processing failed." -ForegroundColor Red
    exit 1
}

# 3. Run Signal Outcome Audit
Write-Host "[*] Auditing Active Signal Outcomes..."
python scripts/maintenance/audit_production_engine.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Signal audit failed." -ForegroundColor Red
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] INTELLIGENCE PROCESSED"
Write-Host "============================================================"
exit 0
