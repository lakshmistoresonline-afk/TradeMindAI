# Implementation Plan - Shadow Outcome Notification Automation

This plan automates the persistence, verification, and reporting of terminal outcomes for Shadow signals. When a signal reaches a terminal state (WIN, LOSS, etc.), the system will automatically generate detailed markdown reports and update cumulative statistics.

## User Review Required

> [!IMPORTANT]
> **AUTOMATION HOOK:** The reporting logic will be integrated into the `ShadowService.audit_open_signals` loop. Every time an outcome is resolved, the database will be updated first, followed by the generation of two markdown files: `SHADOW_OUTCOME_<id>.md` and `SHADOW_LATEST_OUTCOME.md`.
>
> **STRATEGY FREEZE:** This change only affects reporting and persistence infrastructure. No trading logic or Strategy v2.2 parameters will be modified.

## Proposed Changes

### 1. Hardened Outcome Persistence & Logging
#### [MODIFY] [shadow_service.py](file:///G:/TradeMindAI/production/shadow/shadow_service.py)
- Update `audit_open_signals` to:
    - Log `OUTCOME_RESOLUTION` events to the `shadow_events` table for every resolved signal.
    - Explicitly handle `OUTCOME_PENDING` for unreliable resolutions.
    - Trigger `ShadowReporter.generate_outcome_reports(sig_id)` immediately after DB commit.

### 2. Automated Outcome Reporting
#### [NEW] [shadow_reporter.py](file:///G:/TradeMindAI/production/reports/shadow_reporter.py)
- Implement `ShadowReporter` class with the following capabilities:
    - `generate_outcome_reports(signal_id)`: Creates the detailed per-signal report.
    - `update_latest_outcome()`: Maintains a summary of the single most recent completed trade.
    - `calculate_completed_count()`: Derived directly from the `shadow_signals` table.

### 3. Integrated Daily Reporting
#### [MODIFY] [generate_shadow_report.py](file:///G:/TradeMindAI/production/reports/generate_shadow_report.py)
- Ensure the `daily_shadow_report.md` automatically includes the latest completed trade status and the `COMPLETED_TRADES / 20` progress bar.

## Verification Plan

### Automated Verification
- **Persistence Check:** After a simulated outcome resolution, the system will be "restarted" to verify the signal remains in its terminal state and the completed trade count is stable.
- **Integrity Check:** `integrity_scan.py` will verify that no fabricated outcomes were created.

### Manual Verification
- **Report Audit:** Inspect `production/reports/SHADOW_OUTCOME_<signal_id>.md` for data accuracy (MFE, MAE, Net Return, etc.).
- **Consistency Check:** Verify that the "Latest Outcome" in the daily report matches the database record.

## Lifecycle Transition
- `ACTIVE` → `TARGET_HIT` (WIN) | `STOP_LOSS` (LOSS) | `EXPIRED` (TIMEOUT) | `OUTCOME_PENDING`
