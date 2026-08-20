# TradeMind AI - Step 4.3 Robustness Validation Runner
Write-Host "--- STEP 4.3 ROBUSTNESS VALIDATION START ---" -ForegroundColor Cyan

$scripts = @(
    "scripts/accuracy/step4_3_timeline_audit.py",
    "scripts/accuracy/step4_3_lookahead_audit.py",
    "scripts/accuracy/step4_3_survivorship_audit.py",
    "scripts/accuracy/step4_3_oos_validation.py",
    "scripts/accuracy/step4_3_robustness_suite.py",
    "scripts/accuracy/step4_3_symbol_sector_robustness.py",
    "scripts/accuracy/step4_3_statistical_validation.py",
    "scripts/accuracy/step4_3_capacity_audit.py",
    "scripts/accuracy/step4_3_data_quality_audit.py",
    "scripts/accuracy/step4_3_robustness_scorecard.py",
    "scripts/accuracy/step4_3_final_verdict.py"
)

foreach ($s in $scripts) {
    Write-Host "[*] Executing $s..." -ForegroundColor Gray
    .venv\Scripts\python.exe $s
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] $s failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "--- STEP 4.3 ROBUSTNESS VALIDATION COMPLETE ---" -ForegroundColor Green
Write-Host "Results generated in docs/step4_3/ and data/results/step4_3/" -ForegroundColor Green
