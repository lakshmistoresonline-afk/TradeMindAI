# PHASE 7.8: CELERY BEAT RUNTIME FORENSIC REPORT

## 1. Executive Summary
The `trademind-beat` role-confusion has been resolved, and Celery Beat is successfully starting. However, a new **Lifecycle Termination** issue has been identified where the container exits approximately 30 seconds after startup. Additionally, the Shadow cycle task is not being dispatched during the observed runtime.

## 2. Forensic Findings

### A. Container Termination Root Cause
- **Missing Port Binding**: In `backend/start.sh`, the `shadow-beat` service branch does not start the dummy HTTP server (`python3 -m http.server $PORT`).
- **Railway Policy**: Railway expects a process to bind to the `$PORT` environment variable if defined. If no port is bound within the timeout window (typically 30-60s), Railway kills the container as "Unhealthy".
- **Evidence**: "Stopping Container" and "Removed" status in logs shortly after successful Beat startup.

### B. Schedule Dispatch Absence
- **Market Hours Alignment**: The `run-shadow-monitoring-cycle` is scheduled for `crontab(minute="*/30", hour="9-16")`. 
- **Time Check**: The current audit was performed around **16:46 IST**. The most recent due cycle was at **16:30 IST**. If the Beat service started *after* 16:30, it would not dispatch the cycle until **17:00 IST** (which is outside the `9-16` range if interpreted strictly as up to 16:59).
- **Execution Evidence**: `shadow-worker-heartbeat` (1-min interval) **WAS** dispatched, proving the scheduler engine is active. The Shadow cycle was likely not "due" during the brief 30-second runtime.

## 3. Infrastructure Audit Matrix

| Component | Expected | Actual | Status |
| :--- | :--- | :--- | :--- |
| **Service Role** | Celery Beat | Celery Beat | **PASS** |
| **Health Check** | Port Binding | **None** | **FAIL** |
| **Heartbeat Dispatch** | Every 60s | Logged | **PASS** |
| **Shadow Cycle Dispatch**| Every 30m | Not Due | **PENDING** |
| **Persistence** | Neon PostgreSQL | No Cloud Sync | **FAIL** |

## 4. Required Remediation
1. **`backend/start.sh`**: Add the dummy HTTP server to the `shadow-beat` branch to satisfy Railway health checks.
2. **`backend/workers/tasks.py`**:
    - Update crontab to `hour="9-18"` to ensure the "Closing Bell" audit (after 15:30 IST) is captured reliably even if deployment occurs late.
    - Explicitly log the "Next Due" time for the Shadow cycle task during startup.

## 5. PC Independence Status
**Verdict:** `PC_INDEPENDENCE_TEST_FAILING` (Infrastructure Liveness Issue)

## 6. Next Steps
1. **Apply Port Fix**: Deploy corrected `start.sh`.
2. **Extended Schedule**: Broaden the hour range to ensure post-market resolution.
3. **Liveness Test**: Confirm Beat stays `ONLINE` for > 5 minutes on Railway.
