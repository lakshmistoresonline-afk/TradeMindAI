# TradeMind AI Historical Data Synchronization
# Step 1B: Historical Candles

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [1B/6] HISTORICAL DATA SYNCHRONIZATION"
Write-Host "============================================================"

# 1. Environment Check
& scripts/windows/00_check_environment.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

# Activate venv
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 2. Run Sync
Write-Host "[*] Starting NIFTY 200 Historical Sync (2020-01-01 to Present)..."
python -m scripts.data.sync_market_history --universe NIFTY_200 --start-date 2020-01-01 --resume
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Historical synchronization failed or incomplete."
    exit 1
}

# 3. Validate Historical Data
Write-Host "[*] Validating historical data coverage..."
python -m scripts.universe.validate_historical
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Historical data validation failed. Check coverage report."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] NIFTY 200 HISTORICAL SYNCHRONIZATION COMPLETE"
Write-Host "============================================================"
exit 0
