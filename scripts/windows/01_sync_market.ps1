# TradeMind AI Market Synchronization (Consolidated v2.2)
$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [1/6] MARKET DATA SYNCHRONIZATION"
Write-Host "============================================================"

# 1. Environment Validation
Write-Host "[*] Phase 1: Environment Validation"
& scripts/windows/00_check_environment.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Aborting: Environment check failed." -ForegroundColor Red
    exit 1
}

# Ensure venv is active
$VENV_PATH = "$(Get-Location)/.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}
$PythonExe = "$VENV_PATH/Scripts/python.exe"

# 2. Schema Initialization
Write-Host "`n[*] Phase 2: Initializing Database Schema..."
& $PythonExe -c "from backend.core.postgres import init_db; init_db()"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Schema initialization failed." -ForegroundColor Red
    exit 1
}
Write-Host "   + Schema: READY"

# 3. Data Forensic Cleanup
Write-Host "`n[*] Phase 3: Performing data forensic cleanup..."
& $PythonExe scripts/maintenance/data_cleanup.py --no-dry-run --confirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Cleanup failed." -ForegroundColor Red
    exit 1
}
Write-Host "   + Cleanup: SUCCESS"

# 4. NIFTY 200 Master Population
Write-Host "`n[*] Phase 4: Synchronizing NIFTY 200 Master..."
& $PythonExe terminal_master_scripts/02_populate_stocks_master.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] NIFTY 200 population failed." -ForegroundColor Red
    exit 1
}

# 5. Universe Validation
Write-Host "`n[*] Phase 5: Validating NIFTY 200 Universe..."
& $PythonExe scripts/universe/validate_nifty200.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] NIFTY 200 validation failed. Universe is incomplete." -ForegroundColor Red
    exit 1
}
Write-Host "   + Universe: PASS"

# 6. F&O Master
Write-Host "`n[*] Phase 6: Seeding derivative instruments..."
& $PythonExe terminal_master_scripts/03_seed_derivative_instruments.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] F&O Seeding failed." -ForegroundColor Red
    exit 1
}

# Validation: Use Python helper for reliable results
$ValidationResults = & $PythonExe scripts/windows/validate_step1.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Final validation failed." -ForegroundColor Red
    exit 1
}

$FoCount = 0
foreach ($line in $ValidationResults) {
    if ($line -match "FO_COUNT: (\d+)") { $FoCount = [int]$matches[1] }
}

if ($FoCount -eq 0) {
    Write-Host "[!] F&O validation failed. No derivative instruments found." -ForegroundColor Red
    exit 1
}
Write-Host "   + F&O Instruments: VERIFIED ($FoCount contracts)"

Write-Host "`n============================================================"
Write-Host " [SUCCESS] MARKET SYNCHRONIZATION COMPLETE" -BackgroundColor DarkGreen -ForegroundColor White
Write-Host "============================================================"
exit 0
