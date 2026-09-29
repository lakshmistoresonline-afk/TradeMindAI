# TradeMind AI — V4 Data Source Audit

---

## 1. Primary Data Sources

| Domain | Source | Refresh Rate | Historical Depth | Status |
| :--- | :--- | :--- | :--- | :--- |
| **NSE Spot Prices** | Yahoo Finance API (`.NS`) | 15 Minutes | 10 Years | Active |
| **Active Signals** | Firestore (`signals`) | Real-Time | Current Open | Active |
| **History Signals** | Firestore (`signals_history`) | Real-Time | 100 Unique Equities | Active |
| **System Heartbeat** | Firestore (`system_metrics/last_price_sync`) | 15 Minutes | Live | Active |

---

## 2. Zero-Fake-Data Integrity Protocol

- No hardcoded market values masquerading as live prices.
- All live spot prices are written to `web/src/utils/livePrices.ts` during each 15-minute background sync.
