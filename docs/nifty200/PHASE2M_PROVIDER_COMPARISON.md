# PHASE 2M: PROVIDER COMPARISON MATRIX (2026)

## 1. Technical Capabilities Matrix

| Provider | NSE Equity | Index Futures | Stock Futures | Index Options | Stock Options | Real-Time LTP | Option Greeks | Historical (F&O) | Expired Contracts | Auth (Data) | Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Upstox API** | PASS | PASS | PASS | PASS | PASS | < 45ms | **Built-in** | PASS | **Yes** | **1-Year Token**| **9.6** |
| **DhanHQ** | PASS | PASS | PASS | PASS | PASS | **< 20ms** | **Built-in** | PASS | **Yes (Rolling)**| Daily | **9.4** |
| **Zerodha Kite**| PASS | PASS | PASS | PASS | PASS | < 100ms | Manual | PASS | No | Daily OAuth | 8.8 |
| **FYERS V3** | PASS | PASS | PASS | PASS | PASS | < 50ms | WIP | PASS | No | Daily | 8.5 |
| **Groww API** | PASS | PASS | PASS | PASS | PASS | < 20ms | Built-in | 3 Months | No | Daily | 8.2 |

## 2. Competitive Advantage Analysis

### **The "Analytics Token" Breakthrough (Upstox)**
Upstox's 2026 Analytics Token is the single most significant factor for TradeMind AI. It enables a 100% autonomous backend monitor that does not require human intervention for daily OAuth redirects. This solves the "Daily Login" bottleneck that previously affected shadow mode reliability.

### **The Forensic King (DhanHQ)**
DhanHQ's ability to fetch data for **expired options** via the Rolling Options API is critical for Phase 2M. It allows TradeMind to forensically audit the 1,195 legacy signals where contracts have already expired, bringing them to a LEVEL 3 verification state.

---
**Final Recommendation**: **Upstox API** (Primary for Live Shadow Feed) + **DhanHQ** (Secondary for Historical Forensic Audit).
