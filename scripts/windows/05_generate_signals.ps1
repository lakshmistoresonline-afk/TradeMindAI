<<<<<<< HEAD
# TradeMind AI Signal Generation
# Step 5: Signals

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [5/6] SIGNAL GENERATION"
Write-Host "============================================================"

# Activate venv
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 1. Generate signals for NIFTY 200
Write-Host "[*] Generating production signals for NIFTY 200..."
python -m scripts.signals.generate_bulk --universe NIFTY_200
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Signal generation failed."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] SIGNALS GENERATED"
=======
# TradeMind AI - Local Signal Generation (P0)
$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host " TRADEMIND AI - STEP 5: LIVE SIGNAL GENERATION"
Write-Host "============================================================"

# [1/1] Master Signal Generation
Write-Host "`n[1/1] Generating Qualified Signals (No-Trade Filter Active)..." -ForegroundColor Cyan
& $PythonExe terminal_master_scripts/04_generate_live_signals.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Live signal generation failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n============================================================"
Write-Host " [SUCCESS] SIGNAL GENERATION COMPLETE"
>>>>>>> origin/main
Write-Host "============================================================"
exit 0
