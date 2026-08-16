# TradeMind AI - Local Data Sync (P0)
$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host " TRADEMIND AI - STEP 1: MARKET DATA SYNCHRONIZATION"
Write-Host "============================================================"

# [1/6] Environment Validation
Write-Host ""
Write-Host "[1/6] Validating execution environment..."
& "$ProjectRoot\scripts\windows\00_check_environment.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Environment validation failed. Aborting." -ForegroundColor Red
    exit 1
}

# [2/6] Data Forensic Cleanup
Write-Host ""
Write-Host "[2/6] Performing data forensic cleanup..."
& $PythonExe scripts/maintenance/data_cleanup.py --no-dry-run --confirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Data cleanup failed." -ForegroundColor Red
    exit 1
}
Write-Host "   + Cleanup: SUCCESS" -ForegroundColor Green

# [3/6] NIFTY 200 Population
Write-Host ""
Write-Host "[3/6] Synchronizing NIFTY 200 Master..."
& $PythonExe scripts/universe/migrate_index_membership.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Index membership migration failed." -ForegroundColor Red
    exit 1
}

& $PythonExe terminal_master_scripts/02_populate_stocks_master.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: NIFTY 200 population failed." -ForegroundColor Red
    exit 1
}

# [4/6] NIFTY 200 Validation
Write-Host ""
Write-Host "[4/6] Validating NIFTY 200 Universe..."
& $PythonExe scripts/universe/validate_nifty200.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: NIFTY 200 validation failed. Universe is incomplete." -ForegroundColor Red
    exit 1
}

# [5/6] F&O Population and Validation
Write-Host ""
Write-Host "[5/6] Seeding and Validating F and O Master..."
& $PythonExe scripts/universe/migrate_instruments_schema.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Instruments schema migration failed." -ForegroundColor Red
    exit 1
}

& $PythonExe terminal_master_scripts/03_seed_derivative_instruments.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: F and O seeding failed." -ForegroundColor Red
    exit 1
}

& $PythonExe scripts/universe/validate_fno.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: F and O master validation failed." -ForegroundColor Red
    exit 1
}

# [6/6] Final Production-State Verification
Write-Host ""
Write-Host "[6/6] Verifying final production state..."
& $PythonExe scripts/windows/validate_step1.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Final validation failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================"
Write-Host " [SUCCESS] MARKET SYNCHRONIZATION COMPLETE"
Write-Host "============================================================"
exit 0
