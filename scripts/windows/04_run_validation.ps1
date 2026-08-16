# TradeMind AI Validation & Backtesting
# Step 4: Validation

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [4/6] QUANTITATIVE VALIDATION (WALK-FORWARD)"
Write-Host "============================================================"

# Activate venv
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 1. Run Walk-Forward Validation
Write-Host "[*] Executing Walk-Forward Validation pipeline..."
python -m scripts.ml.walk_forward_validation
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Validation pipeline failed."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] VALIDATION COMPLETE"
Write-Host "============================================================"
exit 0
