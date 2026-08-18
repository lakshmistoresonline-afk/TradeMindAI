# TradeMind AI Environment Validation (Consolidated v2.2)
$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [0/6] ENVIRONMENT VALIDATION"
Write-Host "============================================================"

# 1. Determine Project Root
$ProjectRoot = Get-Location
Write-Host "[*] Project Root: $ProjectRoot"

# 2. Check Python
try {
    $pythonVersion = python --version
    Write-Host "[+] Python version: $pythonVersion"
} catch {
    Write-Host "[!] ERROR: Python not found in PATH."
    exit 1
}

# 3. Virtual Environment Management
$VENV_PATH = "$ProjectRoot/.venv"
if (-not (Test-Path $VENV_PATH)) {
    Write-Host "[*] Creating virtual environment (.venv)..."
    python -m venv .venv
}

Write-Host "[+] Activating virtual environment..."
# Check for activation script
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
} else {
    Write-Host "[!] ERROR: Activation script not found at $VENV_PATH/Scripts/Activate.ps1"
    exit 1
}

# 4. Dependency Check/Install
Write-Host "[*] Checking/Installing production dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Dependency installation failed."
    exit 1
}
Write-Host "   + Dependencies: VERIFIED" -ForegroundColor Green

# 5. Environment Variables
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
Write-Host "   + Environment: OK" -ForegroundColor Green

# 6. Database Connectivity
Write-Host "[*] Testing database connectivity..."
# Use python from venv explicitly to avoid any ambiguity
$PythonVenv = "$VENV_PATH/Scripts/python.exe"
$ConnScript = "import os; from dotenv import load_dotenv; from sqlalchemy import create_engine, text; load_dotenv('backend/.env'); db_url = os.getenv('POSTGRES_URL') or os.getenv('DATABASE_URL') or 'sqlite:///backend/local_operational.db'; engine = create_engine(db_url); conn = engine.connect(); conn.execute(text('SELECT 1')); conn.close(); print('SUCCESS')"
$ConnTest = & $PythonVenv -c $ConnScript 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Database connectivity failed." -ForegroundColor Red
    Write-Host $ConnTest
    exit 1
}
Write-Host "   + Database: CONNECTED" -ForegroundColor Green

# 7. Universe Definition
if (-not (Test-Path "scripts/universe/nifty200_canonical.py")) {
    Write-Host "[!] ERROR: NIFTY 200 canonical universe definition missing."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] ENVIRONMENT READY"
Write-Host "============================================================"
exit 0
