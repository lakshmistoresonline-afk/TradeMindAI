<<<<<<< HEAD
# TradeMind AI Environment Validation
# Step 0: Environment

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [0/6] ENVIRONMENT VALIDATION"
Write-Host "============================================================"

# 1. Check Python
try {
    $pythonVersion = python --version
    Write-Host "[+] Python version: $pythonVersion"
} catch {
    Write-Host "[!] ERROR: Python not found in PATH."
    exit 1
}

# 2. Virtual Environment Management
if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating virtual environment (.venv)..."
    python -m venv .venv
}

Write-Host "[+] Activating virtual environment..."
& .venv/Scripts/Activate.ps1

# 3. Dependency Check/Install
Write-Host "[*] Checking/Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Dependency installation failed."
    exit 1
}

# 4. Environment Variables
Write-Host "[*] Checking environment variables..."
if (-not (Test-Path "backend/.env")) {
    if (Test-Path "backend/.env.example") {
        Write-Host "[!] backend/.env missing. Copying from .env.example..."
        Copy-Item "backend/.env.example" "backend/.env"
    } else {
        Write-Host "[!] ERROR: backend/.env and .env.example missing."
        exit 1
    }
}

# 5. Database Connectivity
Write-Host "[*] Testing database connectivity..."
python -m scripts.maintenance.check_db_connectivity
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Database connectivity failed."
    exit 1
}

# 6. NIFTY 200 Universe Check
Write-Host "[*] Checking NIFTY 200 Universe definition..."
if (-not (Test-Path "scripts/universe/nifty200_canonical.py")) {
    Write-Host "[!] ERROR: NIFTY 200 canonical universe definition missing."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] ENVIRONMENT VALIDATED"
Write-Host "============================================================"
=======
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
>>>>>>> origin/main
exit 0
