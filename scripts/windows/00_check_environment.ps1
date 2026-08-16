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
exit 0
