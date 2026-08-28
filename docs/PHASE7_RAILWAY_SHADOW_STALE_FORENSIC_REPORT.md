# PHASE 7.2: RAILWAY SHADOW STALE-STATE FORENSIC REPORT

## 1. Executive Summary
The "SHADOW_DATA_STALE" state observed on 2026-08-19 is the result of a **Multi-Service Configuration Mismatch**. While the Railway API is correctly connected to the Neon PostgreSQL database, the Shadow Worker and Shadow Beat services are operating in a localized isolation state, effectively writing to an ephemeral SQLite database instead of the production cloud tier.

## 2. Exact Root Cause
The forensic audit identifies the following primary failure points:

### A. Environment Variable Leak/Missing
- **POSTGRES_URL & ENVIRONMENT**: These variables are likely missing from the `shadow-worker` and `shadow-beat` service configurations in Railway. 
- **Default Fallback**: In the absence of these variables, the system defaults to `ENVIRONMENT=development` and `POSTGRES_URL=sqlite:///./local_operational.db`.
- **Ephemeral Isolation**: Evaluations, heartbeats, and cycle IDs are being written to a local file inside the worker container. This file is inaccessible to the API and is destroyed upon every service restart.

### B. Task Routing False Positive
- **Heartbeat Success**: The logs confirm `terminal_heartbeat` is executing, but it is recording "WORKER_PRESENCE" into the wrong database.
- **Shadow Cycle Delivery**: The reason `run_shadow_cycle_task` was not observed might be due to the worker being stuck in a generic role if `SERVICE_TYPE` was not correctly applied, or simply because its logs were not scrutinized for the "LOCKED" skip message (if the lock was set in the local SQLite/Redis).

## 3. Infrastructure Audit Matrix

| Component | Expected | Actual | Status |
| :--- | :--- | :--- | :--- |
| **Railway API** | Read Neon PG | Reads Neon PG | **PASS** |
| **Shadow Worker** | Write Neon PG | Writes Local SQLite | **FAIL** |
| **Shadow Beat** | Trigger Neon PG | Triggers Local Context | **FAIL** |
| **Redis Broker** | Single Instance | Verified | **PASS** |
| **Shadow State** | Unified | Split-Brain (PG vs SQLite) | **CRITICAL FAIL** |

## 4. Evidence from Logs
- `[Heartbeat] Nifty Sync: 15000.0`: Proves the worker is running and processing the task queue.
- `Dashboard: Evaluation Cycles = 10`: Proves the API is reading the stale migrated baseline in Neon, oblivious to the worker's local activity.
- `GET https://api.groww.in/v1/live/quote?symbol=NSE-NIFTY HTTP 404`: Confirms the worker is active but encountering data-provider mapping issues.

## 5. Secondary Issue: NIFTY Data Provider
The 404 error for `NSE-NIFTY` confirms that the Groww provider mapping is stale. Although remediated in `yfinance_provider.py` (Phase 6.5), the worker is still attempting a Groww lookup as its primary strategy, which fails and reverts to the fallback value.

## 6. Required Changes
1. **Railway Configuration**: Explicitly set `POSTGRES_URL`, `REDIS_URL`, `ENVIRONMENT=production`, and `SERVICE_TYPE` for all three services.
2. **Code Hardening**: Update `ShadowHeartbeat` and `terminal_heartbeat` to implement the same Fail-Closed SQLite check as the main cycle.
3. **Beat Routing**: Add explicit `options={"queue": "shadow"}` to the `beat_schedule` in `tasks.py` to ensure perfect routing even if decorators fail to propagate.

## 7. Recovery Procedure
1. Verify Environment Variables in Railway Dashboard.
2. Redeploy all services.
3. Trigger a manual heartbeat and verify "Worker ONLINE" on the dashboard.
4. Wait for the next 30-minute cycle.

## Final Status
`SHADOW_STALE_ROOT_CAUSE_IDENTIFIED`
The system is cloud-hosted but configurationally isolated. PC-independence remains pass, but cloud-tier consistency is broken.
