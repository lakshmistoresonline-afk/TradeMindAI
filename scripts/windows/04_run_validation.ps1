# TradeMind AI Master Quantitative Validation Pipeline
# Vision 2.2: Forensic Real-Data Validation

$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " TRADEMIND AI - MASTER QUANTITATIVE VALIDATION"
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Environment & Database Check
Write-Host "`n[1/6] VERIFYING INFRASTRUCTURE..." -ForegroundColor Yellow
python scripts/validate_schema.py
if ($LASTEXITCODE -ne 0) { Write-Host "[!] Schema validation failed." -ForegroundColor Red }

# 2. Universe & Coverage Audit
Write-Host "`n[2/6] AUDITING UNIVERSE & DATA COVERAGE..." -ForegroundColor Yellow
python scripts/universe/generate_universe_report.py
python scripts/universe/validate_historical.py
if ($LASTEXITCODE -ne 0) { Write-Host "[!] Data coverage requirements not met." -ForegroundColor Red }

# 3. F&O Master Validation
Write-Host "`n[3/6] VALIDATING F&O INSTRUMENTS..." -ForegroundColor Yellow
python scripts/universe/validate_fno.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] F&O Validation failed or blocked." -ForegroundColor Yellow
}

# 4. Out-of-Sample Quantitative Validation (Walk-Forward)
Write-Host "`n[4/6] RUNNING OOS WALK-FORWARD VALIDATION..." -ForegroundColor Yellow
python scripts/accuracy/walk_forward_v2.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Walk-Forward validation failed." -ForegroundColor Red
}

# 5. Economic & Failure Mode Analysis
Write-Host "`n[5/6] RUNNING ECONOMIC & FAILURE DIAGNOSTICS..." -ForegroundColor Yellow
python scripts/accuracy/strategy_diagnostics.py
python scripts/accuracy/economic_analyzer.py
python scripts/accuracy/failure_mode_deep_dive.py

# 6. Final Report Generation
Write-Host "`n[6/6] GENERATING FINAL VALIDATION ARTIFACTS..." -ForegroundColor Yellow
if (Test-Path "QUANTITATIVE_VALIDATION_FINAL_REPORT.md") {
    Write-Host "[SUCCESS] Final Report Generated: QUANTITATIVE_VALIDATION_FINAL_REPORT.md" -ForegroundColor Green
}

Write-Host "`n============================================================" -ForegroundColor Cyan
if ($VALIDATION_FAILED) {
    Write-Host " VALIDATION STATUS: FAIL / BLOCKED" -ForegroundColor Red
    exit 1
} else {
    Write-Host " VALIDATION STATUS: PASS (EVIDENCE-BACKED)" -ForegroundColor Green
    exit 0
}
