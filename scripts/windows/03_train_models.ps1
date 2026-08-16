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
Write-Host "============================================================"
exit 0
