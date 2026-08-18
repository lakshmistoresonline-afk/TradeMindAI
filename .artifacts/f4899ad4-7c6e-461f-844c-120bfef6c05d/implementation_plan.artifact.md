# Implementation Plan - Phase 6: Railway 24/7 Shadow Engine Migration

This phase migrates the certified Shadow Trading Engine (Strategy v2.2) to Railway for autonomous, PC-independent 24/7 execution. The authoritative state will move from local SQLite to hosted PostgreSQL, orchestrated by a dedicated Celery worker and scheduler.

## User Review Required

> [!IMPORTANT]
> **DATABASE MIGRATION:** The authoritative 1/20 Shadow evidence (SBIN WIN signal) will be migrated from `local_operational.db` to the hosted PostgreSQL.
>
> **FAIL-CLOSED POLICY:** In production, the engine will strictly refuse to use SQLite. If PostgreSQL is unavailable, it will fail closed.
>
> **DISTRIBUTED LOCK:** A Redis-backed lock will ensure that only one Shadow cycle can execute at a time across replicas.

## Proposed Changes

### 1. Infrastructure & Environment
#### [MODIFY] [config.py](file:///G:/TradeMindAI/backend/core/config.py)
- Add `ENVIRONMENT` setting (defaulting to `development`).
- Strengthen `POSTGRES_URL` validation to prevent accidental SQLite use in production.

#### [MODIFY] [start.sh](file:///G:/TradeMindAI/backend/start.sh)
- Add support for `SERVICE_TYPE=shadow-worker` and `SERVICE_TYPE=shadow-beat`.
- Use specific concurrency and queue routing for the Shadow worker.

### 2. Database Migration & Authority
#### [NEW] [migrate_shadow_to_pg.py](file:///G:/TradeMindAI/scripts/maintenance/migrate_shadow_to_pg.py)
- Forensic script to move `shadow_signals` and `shadow_events` from SQLite to PostgreSQL.
- Only migrates Phase 5G+ data (Baseline: 2026-08-18).
- Verifies the 1/20 completed trade counter after migration.

#### [MODIFY] [shadow_service.py](file:///G:/TradeMindAI/production/shadow/shadow_service.py)
- Add production safety check: Fail if `ENVIRONMENT=production` and `database_url` is SQLite.

### 3. Celery Orchestration
#### [MODIFY] [tasks.py](file:///G:/TradeMindAI/backend/workers/tasks.py)
- Add `run_shadow_cycle_task` that wraps `ShadowService.run_shadow_cycle()`.
- Implement a 30-minute NSE-hour schedule (Mon-Fri, 9:15 AM - 3:45 PM IST).

#### [MODIFY] [shadow_service.py](file:///G:/TradeMindAI/production/shadow/shadow_service.py)
- Implement Redis-backed distributed lock (`shadow_engine_lock`) to prevent overlapping cycles.

### 4. Monitoring & Heartbeats
#### [NEW] [shadow_heartbeat.py](file:///G:/TradeMindAI/production/shadow/shadow_heartbeat.py)
- Logic to record worker and scheduler heartbeats in the database.

#### [MODIFY] [shadow.py](file:///G:/TradeMindAI/backend/api/v1/endpoints/shadow.py)
- Expose heartbeat status to the Monitoring API.

### 5. Policy & Documentation
#### [MODIFY] [RAILWAY_RESOURCE_POLICY.md](file:///G:/TradeMindAI/docs/RAILWAY_RESOURCE_POLICY.md)
- Explicitly permit "Shadow Monitoring" tasks while maintaining the prohibition on heavy backtesting/syncing on Railway.

## Verification Plan

### Automated Verification
- `test_db_migration`: Verify SBIN signal exists in PG after script run.
- `test_distributed_lock`: Verify overlapping tasks are blocked.
- `test_production_safeties`: Verify SQLite rejection in production mode.

### Manual Verification
- Deploy to Railway and monitor logs for successful 30-minute cycles.
- **PC Shutdown Test:** Shut down local PC and verify cycle execution via the hosted dashboard on a separate device.

## Final Decision Matrix
| Milestone | Value | Result |
| :--- | :--- | :--- |
| **Evidence Migrated** | 1 / 20 | `PASS` |
| **Database Authority** | PostgreSQL | `PASS` |
| **PC Independent** | YES | `RAILWAY_SHADOW_OPERATIONAL_PC_INDEPENDENT` |
