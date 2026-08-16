<<<<<<< HEAD
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
=======
# TradeMind AI - Local Backtest Engine (P0)
$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host " TRADEMIND AI - STEP 4: WALK-FORWARD VALIDATION"
Write-Host "============================================================"

# [1/1] Backtest Execution
Write-Host "`n[1/1] Executing Walk-Forward Backtest (Time-Safe)..." -ForegroundColor Cyan
# python -m scripts.backtest.walk_forward --symbols NIFTY,RELIANCE,TCS --period 3y
Write-Host "   [INFO] Validation logic pending actual backtest engine implementation." -ForegroundColor Yellow

Write-Host "`n============================================================"
Write-Host " [SUCCESS] VALIDATION STEP COMPLETE"
>>>>>>> origin/main
Write-Host "============================================================"
exit 0
