# TradeMind AI - Local Signal Generation (P0)
$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host " TRADEMIND AI - STEP 5: LIVE SIGNAL GENERATION"
Write-Host "============================================================"

# [1/1] Master Signal Generation
Write-Host "`n[1/1] Generating Qualified Signals (No-Trade Filter Active)..." -ForegroundColor Cyan
& $PythonExe terminal_master_scripts/04_generate_live_signals.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Live signal generation failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n============================================================"
Write-Host " [SUCCESS] SIGNAL GENERATION COMPLETE"
Write-Host "============================================================"
exit 0
