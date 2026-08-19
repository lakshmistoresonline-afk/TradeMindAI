# Implementation Plan - Phase 7: Autonomous Shadow Accumulation & Continuous Validation

This phase establishes the continuous monitoring and validation framework for the now PC-independent Shadow Engine (Strategy v2.2) on Railway. The primary goal is the natural accumulation of 20 genuine completed trades while maintaining 100% operational integrity and strategy freeze.

## User Review Required

> [!IMPORTANT]
> **NO MANUAL INTERVENTION:** The system is now fully autonomous. We will not manually trigger cycles or resolve outcomes unless a systemic failure is detected.
>
> **20-TRADE MILESTONE:** This is the hard project gate. Paper Trading certification will only be initiated after the 20th genuine terminal outcome is audited and reported.
>
> **STRATEGY FREEZE:** Strategy v2.2 parameters (3% Target/Stop, 0.52 Prob, 10M Liquidity) are non-negotiable and strictly enforced by the cloud worker.

## Proposed Changes

### 1. Continuous Reporting & Progress Tracking
#### [MODIFY] [generate_shadow_report.py](file:///G:/TradeMindAI/production/reports/generate_shadow_report.py)
- Refine to support "Phase 7" context.
- Ensure all metrics are derived from Neon PostgreSQL.
- Add "PC Independence" health check to the markdown report.

### 2. Autonomous Monitoring Report
#### [NEW] [PHASE7_AUTONOMOUS_SHADOW_MONITORING_REPORT.md](file:///G:/TradeMindAI/production/reports/PHASE7_AUTONOMOUS_SHADOW_MONITORING_REPORT.md)
- Template for continuous tracking of Phase 7 progress.
- Includes cycle logs, signal audits, and drift metrics.

### 3. Integrity & Heartbeat Automation
#### [RUN] Cloud-Side Monitoring
- The existing `shadow-worker` and `shadow-beat` on Railway already record heartbeats and evaluation events.
- Verification will be done periodically by querying the Cloud API.

### 4. Outcome Resolution Automation
- **Status:** Already implemented in `ShadowService`. Resolves ACTIVE signals naturally against subsequent market candles.

## Verification Plan

### Automated Monitoring (Cloud)
- **Cycle Count Monitoring:** Verify `evaluation_cycles` increment every 30 minutes (NSE Hours).
- **Heartbeat Audit:** Verify `shadow_worker` and `shadow_beat` show `ONLINE` status in the web dashboard.
- **Drift Audit:** Verify Probability Mean remains within ±0.05 of the 0.587 baseline.

### Manual Acceptance Test
- **Dashboard Review:** Periodic inspection of [https://com-webcraft-trademindai-c8f75.web.app/shadow](https://com-webcraft-trademindai-c8f75.web.app/shadow).
- **Milestone Verification:** Generate a milestone report (`SHADOW_MILESTONE_05`, etc.) as soon as the completed trade count advances.

## Milestone Horizon
| Milestone | Completed Trades | Expectation |
| :--- | :--- | :--- |
| **Current** | 1 / 20 | Baseline established (SBIN WIN). |
| **M1** | 5 / 20 | First statistical confidence check. |
| **M2** | 10 / 20 | Mid-horizon audit. |
| **M3** | 15 / 20 | Final pre-gate audit. |
| **M4** | 20 / 20 | **PHASE 7 COMPLETE - SHADOW-TO-PAPER GATE**. |
