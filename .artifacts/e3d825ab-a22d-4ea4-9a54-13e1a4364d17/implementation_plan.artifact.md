# Implementation Plan - FIREBASE QUOTA-SAFE FINAL DATA SYNCHRONIZATION

This plan implements a robust, quota-aware synchronization engine for TradeMind AI to handle Firestore free-tier limits while ensuring the dashboard remains fully operational.

## 1. Objectives
- **Quota Safety**: Implement `QUOTA_SAFE_MODE` with a daily write ceiling and automatic 429 error detection.
- **Incremental Sync**: Use a persistent JSON queue (`data/firebase/firebase_sync_queue.json`) to track pending writes.
- **Upsert Optimization**: Implement a "Check-Before-Write" strategy to skip redundant updates, saving critical quota.
- **Data Tiering**: Categorize data into Tier 1 (Vital), Tier 2 (Historical), and Tier 3 (Local Archive).

## 2. Data Tiering Strategy

### Tier 1 — VITAL (Always Priority)
- `system_status/latest`: Current market and sync status.
- `performance_summary/*`: KPIs for all validation phases.
- `stocks/*`: Symbol master (excluding full price history).
- `market_regimes`: Latest record.
- `shadow_signals` & `shadow_summary`: Active monitoring data.

### Tier 2 — HISTORICAL (Sync as Quota Allows)
- `portfolio_equity`: Backtest and shadow equity curves.
- `market_regimes`: Historical classification history.
- `stocks/{symbol}/prices`: Latest 30-100 bars for dashboard charts.

### Tier 3 — LOCAL ARCHIVE (Do Not Sync)
- Full 1M+ `historical_prices` (Dashboard uses EOD/Recent only).
- Raw 37,876 Step 4.2 backtest signals (Archived for research).

## 3. Proposed Changes

### [NEW] [data/firebase/firebase_sync_queue.json](file:///G:/TradeMindAI/data/firebase/firebase_sync_queue.json)
- Persistent store for pending sync operations.
- Tracks symbol, date, collection, document ID, and status.

### [NEW] [scripts/accuracy/sync_quota_safe.py](file:///G:/TradeMindAI/scripts/accuracy/sync_quota_safe.py)
- Quota-aware Python sync engine.
- Configurable `BATCH_SIZE` (default 50) and `MAX_WRITES_PER_RUN`.
- Implements `get_doc` comparison before `set_doc`.
- Gracefully handles `RESOURCE_EXHAUSTED` by persisting the queue and stopping.

### [NEW] [scripts/windows/FIREBASE_QUOTA_SAFE_SYNC.ps1](file:///G:/TradeMindAI/scripts/windows/FIREBASE_QUOTA_SAFE_SYNC.ps1)
- PowerShell runner that validates environment and triggers the safe sync engine.

### [REGENERATE] [docs/firebase/FIREBASE_COMPLETE_DATA_INVENTORY.md](file:///G:/TradeMindAI/docs/firebase/FIREBASE_COMPLETE_DATA_INVENTORY.md)
- Replace all "PENDING" status with forensic counts.

## 4. Verification Plan

### Automated Tests
- Run sync with `MAX_WRITES_PER_RUN=5` to verify queue persistence and resumption.
- Assert that identical data does not trigger a Firestore write count increase (simulated via logging).

### Manual Verification
- Verify the `shadow_summary` and `system_status` documents in the Firebase Console after a "Vital" sync run.

## 5. Constraints
- **Frozen Strategy**: No logic changes to v2.2.
- **Local Sovereignty**: All generation and sync logic runs strictly on local Windows.
