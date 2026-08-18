# TradeMind AI Market Synchronization (Consolidated v2.2)
$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [1/6] MARKET DATA SYNCHRONIZATION"
Write-Host "============================================================"

# 1. Environment Validation
& scripts/windows/00_check_environment.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

# Activate venv
$VENV_PATH = "$(Get-Location)/.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 2. Schema Initialization
Write-Host "[*] Initializing Database Schema..."
python -c "from backend.core.postgres import init_db; init_db()"
if ($LASTEXITCODE -ne 0) { exit 1 }

# 3. Data Forensic Cleanup
Write-Host "[*] Performing data forensic cleanup..."
python -m scripts.maintenance.data_cleanup --no-dry-run --confirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Cleanup failed. Continuing anyway if not critical." -ForegroundColor Yellow
}

# 4. NIFTY 200 Master Population
Write-Host "[*] Synchronizing NIFTY 200 Master..."
python terminal_master_scripts/02_populate_stocks_master.py
if ($LASTEXITCODE -ne 0) { exit 1 }

# 5. Universe Validation
Write-Host "[*] Validating NIFTY 200 Universe..."
python scripts/universe/validate_nifty200.py
if ($LASTEXITCODE -ne 0) { exit 1 }

# 6. F&O Master
Write-Host "[*] Seeding derivative instruments..."
python terminal_master_scripts/03_seed_derivative_instruments.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] F&O Seeding failed. F&O coverage will be restricted." -ForegroundColor Yellow
}

# 7. Historical Data Sync (Triggered via separate script for clarity)
Write-Host "[*] Starting historical data sync..."
& scripts/windows/01B_sync_historical.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "============================================================"
Write-Host " [SUCCESS] MARKET DATA READY"
Write-Host "============================================================"
exit 0
