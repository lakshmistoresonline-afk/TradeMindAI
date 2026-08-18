# TradeMind AI ML Training (Consolidated v2.2)
$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [3/6] MACHINE LEARNING TRAINING"
Write-Host "============================================================"

# 1. Environment Validation
& scripts/windows/00_check_environment.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

# Activate venv
$VENV_PATH = "$(Get-Location)/.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 2. Feature Backfill
Write-Host "[*] Backfilling 11-feature vectors for universe..."
python scripts/ml/backfill_features.py
if ($LASTEXITCODE -ne 0) { exit 1 }

# 3. Train models for NIFTY 200
Write-Host "[*] Training Champion models (Strategy v2.2) for NIFTY 200..."
python scripts/ml/train_nifty200.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: ML Training failed." -ForegroundColor Red
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] MODELS TRAINED AND REGISTERED"
Write-Host "============================================================"
exit 0
