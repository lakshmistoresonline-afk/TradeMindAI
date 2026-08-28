# TradeMind AI Signal Generation (Consolidated v2.2)
$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [5/6] SIGNAL GENERATION"
Write-Host "============================================================"

# 1. Environment Validation
& scripts/windows/00_check_environment.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

# Activate venv
$VENV_PATH = "$(Get-Location)/.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 2. Master Signal Generation
Write-Host "[*] Generating Qualified Signals (Strategy v2.2)..."
python terminal_master_scripts/04_generate_live_signals.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Live signal generation failed." -ForegroundColor Red
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] SIGNAL GENERATION COMPLETE"
Write-Host "============================================================"
exit 0
