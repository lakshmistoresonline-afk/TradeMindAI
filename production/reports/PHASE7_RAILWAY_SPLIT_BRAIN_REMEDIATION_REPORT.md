# PHASE 7.3: RAILWAY SPLIT-BRAIN REMEDIATION REPORT

## 1. Executive Summary
This report documents the identification and remediation of a critical production "Split-Brain" issue where background services (Worker and Beat) were falling back to local SQLite while the API used the authoritative Neon PostgreSQL database. This caused Shadow cycles to disappear and heartbeats to fail.

## 2. Root Cause Analysis
- **Service Isolation**: Shadow Worker and Beat services were deployed without the necessary `POSTGRES_URL` and `ENVIRONMENT=production` variables, triggering a default fallback to ephemeral SQLite files.
- **Silent Failure**: The previous database initialization logic silently reverted to SQLite if PostgreSQL was unavailable, leading to a state where the API and Worker were effectively looking at two different systems.

## 3. Remediation Strategy (Implemented)

### A. Fail-Closed Production Configuration
Modified `backend/core/postgres.py` to enforce a hard rule:
- If `ENVIRONMENT == "production"`, the system **MUST** use PostgreSQL.
- If `POSTGRES_URL` is missing or points to SQLite in production, the service will raise a `RuntimeError` and exit.
- **Silent fallbacks are now strictly forbidden in production.**

### B. Startup Configuration Validation
Modified `backend/start.sh` to include a validation block:
- Verifies `POSTGRES_URL`, `REDIS_URL`, and `ENVIRONMENT` variables.
- Verifies `SERVICE_TYPE` specific requirements.
- Exits non-zero if production variables are missing.

### C. Hardened Heartbeat & Task Routing
- **Heartbeat Safety**: `ShadowHeartbeat` and `terminal_heartbeat` now implement the same fail-closed check, ensuring "Worker ONLINE" status is only reported if persisted to the authoritative Neon database.
- **Beat Routing**: Explicitly routed `run_shadow_cycle_task` and `terminal_heartbeat` to the `shadow` queue in the beat schedule.

### D. NIFTY Data Provider Repair
- Standardized on `NIFTY_50.NS` for yfinance/YahooQuery lookups.
- Added resiliency to `terminal_heartbeat` to handle provider-side delisting errors without crashing the task.

## 4. Verification Plan

### Milestone 1: Startup Refusal
- [ ] Temporarily remove `POSTGRES_URL` from local environment and verify service refusal.

### Milestone 2: Cloud Sync
- [ ] Deploy changes to Railway.
- [ ] Verify "PRODUCTION CONFIGURATION VALIDATED" appears in service logs.
- [ ] Verify Dashboard shows "ENGINE: ONLINE" only after successful Neon write.

### Milestone 3: Split-Brain Resolution
- [ ] Verify `evaluation_cycles` increments on the hosted dashboard (Target: 11+).

## Final Verdict
`RAILWAY_SHADOW_SPLIT_BRAIN_FIXED_PENDING_CYCLE`
The infrastructure is now hardened against silent fallbacks and isolation. Autonomous accumulation is ready to resume.
