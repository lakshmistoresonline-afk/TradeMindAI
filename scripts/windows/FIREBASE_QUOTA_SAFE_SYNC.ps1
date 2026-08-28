# TradeMind AI - Firebase Quota-Safe Synchronization Runner
Write-Host "============================================================" -ForegroundColor White
Write-Host " TRADEMIND AI - FIREBASE QUOTA-SAFE SYNC" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor White

$python = ".venv\Scripts\python.exe"

# 1. Environment Check
Write-Host "[1] Checking Environment..." -ForegroundColor Gray
if (!(Test-Path $python)) { Write-Host "[FAIL] Virtual environment not found." -ForegroundColor Red; exit 1 }

# 2. Run Quota-Safe Sync
# (Assumes queue was built or uses existing one)
Write-Host "[2] Executing Incremental Sync (Resume from Queue)..." -ForegroundColor Gray
& $python scripts/accuracy/sync_quota_safe.py
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Sync engine critical failure." -ForegroundColor Red; exit 1 }

# 3. Report Status
Write-Host "[3] Sync Queue Status:" -ForegroundColor Gray
& $python -c "import json; from pathlib import Path; q = json.load(open('data/firebase/firebase_sync_queue.json')); print(f'Pending: {len(q[\"pending\"])} | Completed: {len(q[\"completed\"])} | Failed: {len(q[\"failed\"])}')"

Write-Host "============================================================" -ForegroundColor White
Write-Host " SYNC SESSION COMPLETE (QUOTA SAFE MODE)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor White
Write-Host "Note: If Quota Exceeded was detected, sync will resume"
Write-Host "automatically upon next execution after quota reset."
Write-Host "============================================================" -ForegroundColor White
