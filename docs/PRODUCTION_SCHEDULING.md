# TradeMindAI — Production Scan Scheduling & Orchestration Guide (Phase 8.4 Audit)

## 1. Overview
TradeMindAI operates as a **BUY-only, signal-only** institutional quantitative terminal. Automated production scans and lifecycle audits execute periodically to evaluate market data, generate Strategy V2.2 signals (with V2.3 research/shadow features isolated), evaluate outcomes, and sync records to the authoritative Neon/PostgreSQL ledger.

---

## 2. Production Invocation & Deployment Configuration

Because TradeMindAI runs as a decoupled containerized service (FastAPI backend on Railway / Cloud Run / Firebase hosting frontend), background scans are orchestrated via standalone worker script execution or external cron triggers:

### Option A: Standalone Worker Execution via CLI (Verified Entry Point)
The authoritative worker script `backend/workers/lifecycle_worker.py` can be executed directly via Python:
```bash
python backend/workers/lifecycle_worker.py
```
This initializes `SignalLifecycleWorker`, runs active signal auditing, multi-horizon signal generation across the validated NSE equity master, and synchronizes with cloud mirrors.

### Option B: Platform Cron Service (Configured Externally)
Configure a scheduled cron job in your deployment platform to invoke the lifecycle worker during NSE trading hours (09:15 to 15:30 IST, which is 03:45 to 10:00 UTC):
```bash
# Example cron schedule (Runs hourly during NSE trading hours, UTC equivalent: 03:45 - 10:00 UTC, Mon-Fri)
45 3-10 * * 1-5 python backend/workers/lifecycle_worker.py
```

*Note: In-process background threading inside FastAPI startup is intentionally unconfigured/absent to prevent multi-worker race conditions and lifespan hazards. Production execution relies on standalone worker script execution or external cron scheduling.*

---

## 3. Overlap Prevention & Idempotency Guarantees
- **Overlap Protection**: The backend guarantees that overlapping scan cycles are prevented through Neon/PostgreSQL active signal locks and atomic database uniqueness constraints (`idx_unique_active_signal` on `live_signals (symbol, timeframe) WHERE status = 'ACTIVE'`).
- **Idempotency**: Duplicate generation attempts for the same active signal identity are safely caught at the database persistence boundary and resolved idempotently.
- **Fail-Closed Safety**: `REAL_TRADING=false`, `LIVE_EXECUTION_ENABLED=false`, and `BROKER_ORDER_EXECUTION_ENABLED=false` remain permanently locked and fail-closed across all scheduled paths.
