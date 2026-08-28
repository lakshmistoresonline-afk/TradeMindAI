# Firebase Full Synchronization Report

## Sync Overview
- **Project ID**: `com-webcraft-trademindai-c8f75`
- **Timestamp**: `2026-08-22 10:45 IST`
- **Method**: Local Python Sync (GCloud Auth)

## Dataset Statistics
| Collection | Record Count | Source | Integrity |
| :--- | :--- | :--- | :--- |
| `stocks` | 202 | Local SQLite `stocks` | 100% |
| `market_regimes` | 1 | Local SQLite `market_regimes` | 100% |
| `live_signals` | 1,089 | Local SQLite `live_signals` | 100% |
| `shadow_signals` | 2 | Local SQLite `shadow_signals` | 100% |
| `shadow_scan_diagnostics` | 400 | Local SQLite `shadow_scan_diagnostics` | 100% |
| `portfolio_equity` | 2,484 | CSV `wf_portfolio_equity.csv` | 100% |
| `performance_summary` | 4 | Step 4.2 / 4.4.2 Baselines | 100% |
| `system_status` | 1 | Runtime Metadata | 100% |

## Key Verifications
- **Stock Status**: 198 symbols marked `OPERATIONAL`, 2 symbols (`GUJGASLTD`, `LTIM`) marked `DATA_UNAVAILABLE`.
- **Validation Separation**: Historical backtest results and walk-forward windows are correctly segregated into `performance_summary/backtest` and `performance_summary/walk_forward`.
- **Latency Tracking**: End-to-end sync of 4,000+ documents completed in < 60s.

**STATUS**: `FIREBASE_DATA_SYNCHRONIZED_AND_VERIFIED`
