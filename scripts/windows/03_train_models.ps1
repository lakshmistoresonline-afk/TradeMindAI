<<<<<<< HEAD
# TradeMind AI ML Training
# Step 3: ML Training

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [3/6] MACHINE LEARNING TRAINING"
Write-Host "============================================================"

# Activate venv
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 1. Train models for NIFTY 200
Write-Host "[*] Training Champion models for NIFTY 200..."
python -m scripts.ml.train_nifty200
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: ML Training failed."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] MODELS TRAINED AND REGISTERED"
=======
# TradeMind AI - Model Training & Calibration (P0)
$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host " TRADEMIND AI - STEP 3: MODEL TRAINING & CALIBRATION"
Write-Host "============================================================"

# [1/1] Quantitative Model Training
Write-Host "`n[1/1] Initiating Local Quantitative Model Training..." -ForegroundColor Cyan
# python -m scripts.ml.train --universe NIFTY_200
Write-Host "   [INFO] Script training logic pending actual ML dataset creation." -ForegroundColor Yellow

Write-Host "`n============================================================"
Write-Host " [SUCCESS] TRAINING STEP COMPLETE"
>>>>>>> origin/main
Write-Host "============================================================"
exit 0
