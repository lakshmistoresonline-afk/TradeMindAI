# STEP 4.2: RUN PORTFOLIO BACKTEST
Write-Host "Starting Portfolio Backtest Engine..." -ForegroundColor Cyan

$pythonScript = "scripts/accuracy/portfolio_simulator.py"

if (Test-Path $pythonScript) {
    python $pythonScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Portfolio Backtest Completed Successfully." -ForegroundColor Green
        Write-Host "Reports generated in docs/ and data/results/" -ForegroundColor Green
    } else {
        Write-Host "Portfolio Backtest Failed with Exit Code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} else {
    Write-Host "Error: $pythonScript not found!" -ForegroundColor Red
    exit 1
}
