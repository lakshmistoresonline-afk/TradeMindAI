# Market Data Freshness Audit: 2026-08-18

## 1. Staleness Summary
The Shadow run detected **10 symbols** with stale data (> 24h old).

## 2. Symbol Report

| Symbol | Last Candle | Expected | Age (hrs) | Status | Error |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GUJGASLTD** | 2026-08-13 | 2026-08-17 | 120+ | CRITICAL | Incomplete history (20 candles) |
| **LTIM** | N/A | 2026-08-17 | INF | BLOCKED | No data from provider |
| **8 Others** | 2026-08-16 | 2026-08-17 | 48 | STALE | Weekend/Holiday overlap vs UTC sync |

## 3. Root Cause
1.  **LTIM Constraint:** Known issue - `yfinance` has intermittent failures for LTIM.NS.
2.  **GUJGASLTD Ingestion Error:** Data gap at provider level during last sync.
3.  **Timezone/Weekend Logic:** The 24h gate is strict. For a run on Tuesday morning (10:54 IST), data from Friday/Monday might be flagged if sync didn't happen exactly within the 24h window relative to UTC.
4.  **Sync Frequency:** `scripts/data/sync_market_history.py` was last run on 2026-08-17 09:32 UTC.

## 4. Remediation
1.  Force re-sync for the NIFTY 200 universe with `--no-resume`.
2.  Maintain 24h gate (DO NOT WEAKEN).
3.  Fix timezone handling in signal engine to account for IST market close.
