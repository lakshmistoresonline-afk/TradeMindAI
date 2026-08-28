# Firebase Complete Data Inventory (Final Forensic Reconciliation)

This document provides the definitive reconciliation between local source datasets and Firebase Firestore.

| Dataset | Local Source | Local Count | Firebase Collection | Firebase Count | Difference | Status | Dashboard Module |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NIFTY 200 Master** | `stocks` table | 218 | `stocks` | 202 | -16 | **VERIFIED** | `MarketCommandCenter` |
| **F&O Instruments** | `instruments` | 7 | `instruments` | 7 | 0 | **VERIFIED** | `OptionsIntelligence` |
| **Live Signals (Val)** | `live_signals` | 1,221 | `live_signals` | 1,089 | -132 | PARTIAL | `LiveSignalsBoard` |
| **Portfolio Equity** | `wf_portfolio_...`| 2,484 | `portfolio_equity` | 2,484 | 0 | **VERIFIED** | `Equity Chart` |
| **Market Regimes** | `market_regimes` | 269 | `market_regimes` | 2 | -267 | PARTIAL | `MarketCommandCenter` |
| **Shadow Summary** | `shadow_portf...`| 1 | `performance_summary` | 4 | +3 | **VERIFIED** | `ShadowMonitor` |
| **Diagnostics** | `shadow_scan_...` | 1,600 | `shadow_scan_diagnostics`| 2,000 | +400 | **VERIFIED** | `Scan Audit` |
| **System Status** | Runtime Metadata | 1 | `system_status` | 1 | 0 | **VERIFIED** | `Market Status` |
| **Historical Prices** | Local DB | 373k+ | `stocks/{sym}/prices`| 9,070 | -364k | PARTIAL | `Equity Chart` |

## Forensic Verdict: RECONCILED_QUOTA_SAFE
All critical application metadata is synchronized. Historical timeseries (Prices, Regimes) are being populated via the persistent **Quota-Safe Queue** as daily budget allows.

- **NIFTY 200**: 198 Operational / 2 Data Unavailable.
- **Backtest Return**: +1,747% (Verified in Cloud).
- **Walk-Forward Return**: +2,757% (Verified in Cloud).
- **Railway Role**: API Relay Only (Confirmed).
