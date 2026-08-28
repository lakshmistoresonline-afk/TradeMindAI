# PHASE 6.4: CELERY SHADOW TASK ROUTING FORENSIC REPORT

## 1. Executive Summary
The PC-independence acceptance test for Phase 6.4 failed due to a **Task Delivery Defect** in the cloud infrastructure. While the system was online, the Beat scheduler and the Shadow Worker were operating in different namespaces and queues, preventing the execution of the 30-minute Shadow cycles.

## 2. Root Cause Analysis
The forensic audit identified three critical infrastructure defects:
1. **Namespace Mismatch:** The Celery app was initialized as `tasks`, but the scheduler was looking for `backend.workers.tasks.*`. This caused the worker to ignore the cloud-triggered tasks.
2. **Queue Isolation:** The Shadow Worker was configured to listen only to the `shadow` queue, but the system's `terminal_heartbeat` (used for dashboard health) was defaulting to the `celery` queue. This gave a false positive "HEALTHY" status while the actual Shadow tasks were stuck in a queue with no listeners.
3. **Data Provider Mapping:** Changes in Yahoo Finance (Aug 2026) caused NIFTY lookups to return 404/Delisted errors, breaking the terminal heartbeat's price discovery.

## 3. Infrastructure Audit Matrix
| Component | Expected | Actual | Status |
| :--- | :--- | :--- | :--- |
| **Celery Beat** | Schedule `backend.*` | Scheduled `backend.*` | **PASS** |
| **Shadow Worker** | Listen to `shadow` | Listened to `shadow` | **PASS** |
| **Task Registration**| `backend.*` | Registered as `tasks.*` | **FAIL** |
| **Heartbeat Queue** | `shadow` | Defaulted to `celery` | **FAIL** |
| **Shadow Cycle** | Executed in cloud | Never received by worker | **FAIL** |

## 4. Remediation Implemented
1. **Standardized Namespace:** Re-initialized Celery with the explicit module name `backend.workers.tasks`.
2. **Hardened Routing:** Explicitly routed **every** Shadow-related task (including heartbeats) to the `shadow` queue.
3. **Resilient Mapping:** Updated NIFTY symbol mapping to `NIFTY_50.NS` to resolve provider delisting errors.
4. **Visibility Integration:** Integrated `ShadowHeartbeat` into the terminal task so the dashboard reflects actual cloud worker presence every 60 seconds.

## 5. PC Independence Status
**Verdict:** `PC_INDEPENDENCE_TEST_PENDING` (Remediated)

## 6. Next Steps
1. **Railway Redeploy:** Trigger a new build to apply the namespace and routing fixes.
2. **Verify Logs:** Confirm `backend.workers.tasks.run_shadow_cycle_task` is received and executed.
3. **Autonomous Verification:** Shut down local PC and monitor for cycle advancement.
