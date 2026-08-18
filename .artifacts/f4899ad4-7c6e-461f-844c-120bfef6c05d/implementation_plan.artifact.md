# Implementation Plan - Phase 5H: Hosted Shadow Monitoring Dashboard

This phase implements a real-time monitoring dashboard in the hosted TradeMind AI web application. It exposes the current state of Strategy v2.2 Shadow Mode, including evaluations, signals, and performance metrics, while maintaining a strict strategy freeze.

## User Review Required

> [!IMPORTANT]
> **READ-ONLY:** The new API and dashboard are strictly read-only. No trading parameters or signal states can be modified via the web interface.
>
> **DATA SYNC:** Since the Shadow Engine runs on local infrastructure with a SQLite database, a synchronization service will push summarized metrics and active signals to **Cloud Firestore** for hosted visibility.
>
> **STRATEGY FREEZE:** Strategy v2.2 parameters (3% Target, 3% Stop, 10M Liquidity) remain locked and visible as "FROZEN" in the UI.

## Proposed Changes

### 1. Backend: Read-Only Shadow API
#### [NEW] [shadow.py](file:///G:/TradeMindAI/backend/api/v1/endpoints/shadow.py)
- Create FastAPI router with the following endpoints:
    - `GET /status`: Overall system health and strategy metadata.
    - `GET /summary`: Cumulative counts (cycles, events, signals, completed trades).
    - `GET /active-signals`: List of currently open shadow trades.
    - `GET /performance`: Descriptive statistics (Win Rate, Net EV) marked as `INSUFFICIENT_SAMPLE` if $< 20$.
    - `GET /universe`: Table of all 200 symbols with their latest decision.

### 2. Synchronization Service
#### [NEW] [shadow_sync_service.py](file:///G:/TradeMindAI/backend/services/shadow_sync_service.py)
- Implement `ShadowSyncService` to push consolidated state from SQLite to Firestore.
- Document: `shadow_monitor/state`
- Payload: Summary metrics, active signal snapshots, and rejection breakdowns.
- Integration: Trigger sync at the end of every `ShadowService.run_shadow_cycle()`.

### 3. Frontend: Shadow Monitoring Dashboard
#### [NEW] [ShadowMonitor.tsx](file:///G:/TradeMindAI/web/src/pages/ShadowMonitor.tsx)
- Create a high-fidelity dashboard using the existing design system (MUI Dark).
- **Components:**
    - **Header:** Status badges (HEALTHY, FROZEN, SAMPLE_ACCUMULATING).
    - **Metric Grid:** 4-col layout for Cycles, Events, Signals, and Completed/20.
    - **Active Signal View:** Card-based display for current exposure (SBIN).
    - **NIFTY 200 Rejection Table:** Searchable list of all constituents with rejection reasons.
    - **Health Monitor:** Status of DB, Models, and Data Freshness.

#### [MODIFY] [App.tsx](file:///G:/TradeMindAI/web/src/App.tsx)
- Register route `/shadow`.
- Add "Shadow Monitor" to the sidebar navigation.

### 4. Security & Compliance
- **Auth:** Require valid JWT for dashboard access.
- **Privacy:** Ensure no sensitive file paths or credentials are synchronized to the cloud.

## Verification Plan

### Automated Tests
- `pytest backend/tests/api/test_shadow_api.py`: Verify read-only constraints.
- `ShadowSyncService` unit test: Verify Firestore payload integrity.

### Manual Verification
- Deploy to Firebase Hosting and verify the dashboard appears at `/shadow`.
- Confirm `SBIN` active signal and `1 / 20` progress are correctly displayed.
- Verify 10M Liquidity rejections are visible in the symbol table.

## Final Status Matrix
| Condition | Decision |
| :--- | :--- |
| End-to-end data flow verified | `WEB_MONITOR_DEPLOYED` |
| Sync failure or auth issue | `WEB_MONITOR_ISSUES_FOUND` |
| Infrastructure blocked | `WEB_MONITOR_BLOCKED` |
