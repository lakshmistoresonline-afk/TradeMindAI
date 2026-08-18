# Implementation Plan - Phase 6.3: Shadow Monitor Reporting Correction

This phase fixes reporting bugs and terminology discrepancies identified in the Phase 6.2 data audit. It ensures that the Shadow Monitor dashboard and daily reports are consistent, accurate, and derive all metrics from the authoritative Neon PostgreSQL database.

## User Review Required

> [!IMPORTANT]
> **METRIC FIX:** The `Strategy Trigger Events` count will be corrected to reflect actual strategy hits (decision = 'TRADE_SIGNAL') rather than total evaluations.
>
> **DATA SOURCE:** All metrics will now be calculated from the database. The `shadow_observations.csv` will no longer be used as a source for statistics, only for human-readable audit logs.

## Proposed Changes

### 1. Backend: Shadow API Corrections
#### [MODIFY] [shadow.py](file:///G:/TradeMindAI/backend/api/v1/endpoints/shadow.py)
- **Fix Summary:** Correct `strategy_trigger_events` to count only `ShadowEventDB` records where `decision == 'TRADE_SIGNAL'`.
- **Add Probability Stats:** Implement a robust probability mean calculation by parsing the `payload_json` from evaluation events in the database.
- **Scope Baseline:** Ensure all counts are scoped to the Phase 5G baseline (>= 2026-08-18).

### 2. Frontend: UI Label & Mapping Alignment
#### [MODIFY] [ShadowMonitor.tsx](file:///G:/TradeMindAI/web/src/pages/ShadowMonitor.tsx)
- Update labels:
    - "TOTAL EVENTS" → "EVALUATION EVENTS"
    - "TRIGGER EVENTS" → "STRATEGY TRIGGER EVENTS"
- Ensure active signal details are correctly mapped from the API.

### 3. Reporting: Alignment
#### [MODIFY] [generate_shadow_report.py](file:///G:/TradeMindAI/production/reports/generate_shadow_report.py)
- Align all calculation logic (Probability Mean, Trigger Count) with the API implementation.
- Standardize on the terminal outcome whitelist (`TARGET_HIT`, `STOP_LOSS`, `TIMEOUT`, `AMBIGUOUS`, `INVALID`).

## Verification Plan

### Automated Verification
- **SQL Audit:** Run manual queries on Neon to verify that the API returned values ($Cycles=10, Triggers=10$) match the raw data.
- **Baseline Check:** Confirm that historical signals from previous baselines are excluded.

### Manual Verification
- **Dashboard Check:** Verify the live Railway dashboard shows corrected labels and values.
- **Regression Check:** Confirm `sig_SBIN_202608180715` still reports `TARGET_HIT` with +2.80% return.
