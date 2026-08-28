# Step 4.5.21: NIFTY 200 Scan Timeout Forensic Report

**Date:** 2026-08-24
**Status:** STEP_4_5_21_NIFTY200_SCAN_STABLE (Optimized)

## 1. Root Cause Identification
The previous NIFTY 200 scan was estimated to take **~31 minutes** per cycle, leading to frequent timeouts and stale data on the dashboard.

| Bottleneck | Description | Impact |
| :--- | :--- | :--- |
| **Redundant SQL Queries** | `generate_signal` was re-fetching stock data and re-calculating drawdown 200 times per scan. | ~400 unnecessary SQL round-trips. |
| **Sequential Processing** | Symbols were processed one-by-one with high per-symbol latency. | Total scan duration exceeded timeout limits. |
| **Heavy Provider Calls** | Calls like `yf.Ticker.info` were taking up to 20s per symbol. | Blocked the engine execution. |
| **Individual SQL Writes** | Every symbol scan was saving a `Prediction` record to Neon. | Increased IO wait time. |

## 2. Timing Breakdown (Post-Optimization)
| Component | Duration (Total) | Status |
| :--- | :--- | :--- |
| **Bulk Metadata Fetch** | ~1.5s | Optimized (1 SQL Query) |
| **NIFTY 200 Scan** | ~200s | Optimized (Sequential Async) |
| **Neon Event Logging** | ~0.5s | Bulk Commit |
| **Firestore Mirroring** | ~12s | Asynchronous / Non-blocking |
| **Total Cycle Duration** | **3.64 Minutes** | **PASS** |

## 3. Improvements Implemented
- **Bulk Pre-fetching:** Replaced 200 `get_stock_by_symbol` calls with one `get_all_stocks` call.
- **Drawdown Caching:** Calculated portfolio drawdown once per cycle instead of per symbol.
- **ML Inference Bypass:** Refactored `predict_with_champion` to accept pre-loaded metadata and disable redundant SQL writes during scans.
- **Async Resilience:** Verified that Firestore mirroring is asynchronous and does not block the engine if quota is exceeded.

## 4. Scan Results (2026-08-24 08:44 UTC)
- **Total constituents:** 200
- **Successful Fetches:** 198
- **Operational:** 198
- **Stale Data:** 112 (Data in local analytical engine older than 24h)
- **Insufficient Liquidity:** 86
- **Valid Signals:** 0
- **Shadow Trades:** 0

> [!NOTE]
> The high number of `STALE_MARKET_DATA` rejections is expected as the engine is currently using historical analytical features. A separate data ingestion task is required to refresh the DuckDB feature store with today's price action.

---

**FINAL VERDICT:** STEP_4_5_21_NIFTY200_SCAN_STABLE
The scan duration has been reduced by ~90%. The engine completes a full NIFTY 200 universe scan in under 4 minutes, well within the 45-minute lock limit.
