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
Write-Host "============================================================"
exit 0
