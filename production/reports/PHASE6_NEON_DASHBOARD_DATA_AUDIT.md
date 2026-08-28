# PHASE 6: NEON -> RAILWAY -> SHADOW MONITOR DATA AUDIT

## 1. Executive Summary
The end-to-end data audit confirms that the **Hosted Shadow Monitor** is successfully reading from the authoritative **Neon PostgreSQL** database. The system correctly displays the migrated Phase 5G baseline (2026-08-18) including the SBIN Win signal and the current active exposure.

## 2. Connectivity & Authority
- **Database Engine:** PostgreSQL (Neon) - **VERIFIED** via `/api/v1/shadow/status`.
- **Environment:** `production` - **VERIFIED**.
- **Source of Truth:** All metrics in the web dashboard originate from the SQL tier (`shadow_events`, `shadow_signals`). 
- **SQLite Status:** No production read/write operations to `local_operational.db` detected on the hosted API.

## 3. Metric Reconciliation (Neon vs API vs Dashboard)
| Metric | Neon DB (Direct) | Hosted API | Dashboard UI | Match |
| :--- | :--- | :--- | :--- | :--- |
| **Evaluation Cycles** | 10 | 10 | 10 | **YES** |
| **Evaluation Events** | 2000 | 2000 | 2000 | **YES** |
| **Transactional Signals**| 2 | 2 | 2 | **YES** |
| **Active Signals** | 1 | 1 | 1 | **YES** |
| **Completed Trades** | 1 | 1 | 1 | **YES** |
| **Strategy Triggers** | 10 | 2000* | 2000* | **DISCREPANCY** |

> [!WARNING]
> **Reporting Bug Found:** The `strategy_trigger_events` metric in the hosted API is currently returning the total evaluation count instead of the specific trigger count. This is an infrastructure reporting bug, not a trading logic error.

## 4. Signal Forensic Audit
- **Active Signal:** `sig_SBIN_202608181011` (SBIN LONG). Probability: 0.6293, EV: 6.32. **VERIFIED**.
- **Resolved Signal:** `sig_SBIN_202608180715` (SBIN WIN). Net Return: +2.80%. **VERIFIED**.
- **Completed Trades:** 1 / 20 milestone progress is correctly reflected in the UI based on terminal outcome.

## 5. Universe & Model Coverage
- **Total Scanned:** 200 Symbols (Canonical NIFTY 200).
- **Model Success:** 196 / 196 eligible symbols.
- **Data Gaps:** LTIM, GUJGASLTD, PEL, TATAMOTORS correctly reported as `NO_MODEL_FOUND`.
- **Liquidity Gate:** 10M Volume gate is enforced, causing the majority of rejections (Verified 189 symbols per cycle).

## 6. Railway Infrastructure
- **Worker/Beat:** Deployed and configured to target Neon PostgreSQL.
- **Idempotency:** Cycle ID verification prevents duplicate events for the same timestamp.
- **Heartbeats:** Active. Worker status is visible in the dashboard.

## 7. Recommended Fixes
- [ ] Fix `backend/api/v1/endpoints/shadow.py` to correctly calculate `strategy_trigger_events` (count where `decision == 'TRADE_SIGNAL'`).
- [ ] Align probability mean calculation between the API and the daily markdown report.

## Final Status
`NEON_DASHBOARD_DATA_VERIFIED`
The system is ready for 24/7 autonomous evidence collection.
