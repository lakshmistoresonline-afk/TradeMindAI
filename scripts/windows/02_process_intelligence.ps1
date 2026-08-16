# TradeMind AI Market Intelligence Processing
# Step 2: Market Intelligence

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " [2/6] MARKET INTELLIGENCE PROCESSING"
Write-Host "============================================================"

# Activate venv
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

# 1. Run Intelligence Engine
Write-Host "[*] Processing Market Intelligence (Regime + Reports)..."
python -m scripts.market_intelligence.process_intelligence
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Intelligence processing failed."
    exit 1
}

# 2. Run Opportunity Scanner
Write-Host "[*] Running NIFTY 200 Opportunity Scanner..."
python -m scripts.signals.refresh_rankings
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR: Opportunity scanning failed."
    exit 1
}

Write-Host "============================================================"
Write-Host " [SUCCESS] INTELLIGENCE PROCESSED"
Write-Host "============================================================"
exit 0
