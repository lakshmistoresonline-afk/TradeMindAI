# DASHBOARD DATA SOURCE AUDIT

## Overview
This audit identifies the authoritative data source for every metric displayed on the TradeMind AI Shadow Dashboard (/shadow).

## Data Path
UI Component -> API Client (web/src/api/client.ts) -> Backend API (backend/api/v1/endpoints/shadow.py) -> **Firestore (Authoritative Source)**

## Metric Audit

| UI Metric | UI Component | API Endpoint | Firestore Collection | Firestore Document/Field |
| :--- | :--- | :--- | :--- | :--- |
| BASELINE START | ShadowMonitor.tsx | /shadow/status | shadow_summary | latest.baseline_start |
| LAST DATA SYNC | ShadowMonitor.tsx | /shadow/health | shadow_summary | latest.last_run |
| EVALUATION CYCLES | MetricCard | /shadow/summary | shadow_summary | latest.evaluation_cycles |
| EVALUATION EVENTS | MetricCard | /shadow/summary | shadow_summary | latest.evaluation_events |
| STRATEGY TRIGGER EVENTS | MetricCard | /shadow/summary | shadow_summary | latest.transactional_signals |
| COMPLETED TRADES | ProgressCard | /shadow/performance | shadow_summary | latest.trade_count |
| ACTIVE SIGNALS | Table | /shadow/active-signals | shadow_signals | collection (status == 'ACTIVE') |
| WIN RATE | PerfRow | /shadow/performance | shadow_summary | latest.win_rate |
| NET EV | PerfRow | /shadow/performance | shadow_summary | latest.realized_pnl / equity |
| PROB MEAN | PerfRow | /shadow/performance | shadow_summary | latest.probability_mean |
| UNIVERSE SCAN AUDIT | Table | /shadow/universe | shadow_scan_diagnostics | latest scan batch |

## Data Source Conclusion
- **CURRENT STATE:** Firestore authoritative (Project: `com-webcraft-trademindai-c8f75`).
- **PREVIOUS STATE:** Legacy SQL source (Obsolete).
- **TARGET STATE:** Firebase Firestore (Reconciled).
