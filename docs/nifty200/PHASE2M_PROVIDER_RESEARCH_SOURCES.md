# PHASE 2M: PROVIDER RESEARCH SOURCES (SEPTEMBER 2026)

## 1. Official Documentation Reference
| Provider | Source URL | API Version | Date Audited |
| :--- | :--- | :--- | :--- |
| **Upstox API** | [upstox.com/developer/api-docs](https://upstox.com/developer/api-docs) | v2.0 / V3 Ticker | 2026-09-07 |
| **DhanHQ** | [dhanhq.co/docs](https://dhanhq.co/docs) | v2.0 | 2026-09-07 |
| **Zerodha Kite** | [kite.trade/docs/connect/v3](https://kite.trade/docs/connect/v3) | v3.0 | 2026-09-07 |
| **FYERS API** | [fyers.in/fyers-api-v3/docs](https://fyers.in/fyers-api-v3/docs) | v3.0 | 2026-09-07 |
| **Groww API** | [groww.in/developer/docs](https://groww.in/developer/docs) | v1.0 | 2026-09-07 |

## 2. Capability Evidence (F&O Primary)

### **Upstox API (V3 Market Data)**
- **Evidence**: 2026 release of the **Analytics Token**.
- **Capability**: Long-lived (1-year) read-only access to market data.
- **F&O Detail**: Built-in Greeks (Delta, Theta, Gamma, Vega) and real-time OI Change per strike.
- **CAS Support**: Native equilibrium price retrieval for Closing Auction Session.

### **DhanHQ (Market Feed)**
- **Evidence**: Rolling Options Data API (2026 Update).
- **Capability**: Retrieval of **expired derivative contracts** by strike offset (ATM +/- N).
- **F&O Detail**: 200-level market depth on WebSockets (Level 3 data).
- **Backtest Fidelity**: Standardized intraday OHLCV for the last 5 years of all NSE F&O.

### **Zerodha Kite Connect**
- **Evidence**: KiteTicker Documentation (revised 2026).
- **Capability**: 3 concurrent WebSocket connections per API Key.
- **Constraint**: No native Greeks API; requires external calculation or separate library.
- **F&O Detail**: Supports up to 3,000 instruments per connection.

---
**Status**: Research Verified. All primary sources confirm that Upstox and Dhan are the current leaders for "Smart" F&O data.
