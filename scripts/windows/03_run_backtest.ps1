# TradeMind AI - Local Backtest Engine
Write-Host "[*] Executing Walk-Forward Validation..." -ForegroundColor Cyan

python -m scripts.backtest.walk_forward --symbols NIFTY,RELIANCE,TCS --period 3y

Write-Host "[SUCCESS] Performance metrics exported to docs/rc3/WALK_FORWARD_VALIDATION.md" -ForegroundColor Green
