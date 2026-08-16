# TradeMind AI Market Synchronization
# Step 1: Market Data

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [1/6] ENVIRONMENT VALIDATION"
Write-Host "============================================================"
& scripts/windows/00_check_environment.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

# Activate venv for this session
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# Ensure schema is up to date
python -m scripts.maintenance.init_db
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "============================================================"
Write-Host " [2/6] DATA FORENSIC CLEANUP"
Write-Host "============================================================"
python -m scripts.maintenance.data_cleanup --no-dry-run --confirm
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "============================================================"
Write-Host " [3/6] NIFTY 200 POPULATION"
Write-Host "============================================================"
python -m terminal_master_scripts.02_populate_stocks_master
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "============================================================"
Write-Host " [4/6] NIFTY 200 VALIDATION"
Write-Host "============================================================"
python -m scripts.universe.validate_nifty200
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "============================================================"
Write-Host " [5/6] F&O POPULATION AND VALIDATION"
Write-Host "============================================================"
python -m scripts.universe.sync_instruments
if ($LASTEXITCODE -ne 0) { exit 1 }

python -m scripts.universe.validate_fno
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "============================================================"
Write-Host " [5B/6] HISTORICAL DATA SYNCHRONIZATION"
Write-Host "============================================================"
& scripts/windows/01B_sync_historical.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "============================================================"
Write-Host " [6/6] FINAL PRODUCTION-STATE VERIFICATION"
Write-Host "============================================================"
# Optional: Add a check for data coverage here if needed
Write-Host "[+] All synchronization gates passed."

Write-Host "============================================================"
Write-Host " [SUCCESS] MARKET SYNCHRONIZATION COMPLETE"
Write-Host "============================================================"
exit 0
