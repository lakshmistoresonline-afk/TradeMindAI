# TradeMind AI - Environment Verification (P0)
$ErrorActionPreference = "Stop"

Write-Host "[*] STEP 0: Verifying Local Execution Environment..."

# 1. Determine Project Root
$ProjectRoot = Get-Location
if (!(Test-Path "$ProjectRoot\backend\venv")) {
    Write-Host "ERROR: Virtual environment not found at backend/venv" -ForegroundColor Red
    exit 1
}

$PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"
if (!(Test-Path $PythonExe)) {
    Write-Host "ERROR: Python executable not found." -ForegroundColor Red
    exit 1
}

# 2. Verify Python Version
$PythonVersion = & $PythonExe --version
Write-Host "   + Python: $PythonVersion"

# 3. Verify Critical Dependencies
$RequiredPackages = @("sqlalchemy", "dotenv", "psycopg2", "pandas", "yfinance")
Write-Host "[*] Checking Python dependencies..."

foreach ($p in $RequiredPackages) {
    & $PythonExe -c "import $p" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $import_check = "import $p"
        if ($p -eq "dotenv") { $import_check = "import dotenv" }
        elseif ($p -eq "psycopg2") { $import_check = "import psycopg2" }

        & $PythonExe -c "$import_check" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Missing dependency: $p" -ForegroundColor Red
            exit 1
        }
    }
    Write-Host "   + $p : VERIFIED"
}

# 4. Verify Environment Variables
Write-Host "[*] Checking environment variables..."
if (!(Test-Path "$ProjectRoot\backend\.env")) {
    Write-Host "ERROR: .env file missing at backend/.env" -ForegroundColor Red
    exit 1
}

$DbUrlFound = $false
$EnvLines = Get-Content "$ProjectRoot\backend\.env"
foreach ($line in $EnvLines) {
    if ($line -like "*DATABASE_URL=*" -or $line -like "*POSTGRES_URL=*") {
        $DbUrlFound = $true
        break
    }
}

if (!$DbUrlFound) {
    Write-Host "ERROR: Database configuration missing in .env" -ForegroundColor Red
    exit 1
}
Write-Host "   + Database Config: SET"

# 5. Test Database Connectivity
Write-Host "[*] Testing database connectivity..."
$ConnScript = "import os; from dotenv import load_dotenv; from sqlalchemy import create_engine, text; load_dotenv('backend/.env'); db_url = os.getenv('POSTGRES_URL') or os.getenv('DATABASE_URL'); engine = create_engine(db_url); conn = engine.connect(); conn.execute(text('SELECT 1')); conn.close(); print('SUCCESS')"
$ConnTest = & $PythonExe -c $ConnScript 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database connection failed." -ForegroundColor Red
    Write-Host $ConnTest
    exit 1
}
Write-Host "   + Database Connection: SUCCESS"

Write-Host "SUCCESS: Environment validation passed." -ForegroundColor Green
exit 0
