# TradeMind AI: Signal Lifecycle Forensic Audit

## 1. Lifecycle State Machine
Verified the 9-state canonical lifecycle for Strategy V2.2:

| State | Definition | Observed Count |
| :--- | :--- | :--- |
| **CREATED** | Signal initial record | 0 (Immediate transition) |
| **WAITING_FOR_ENTRY**| Price has not hit entry level | 33 |
| **TRIGGERED** | Entry level hit | 0 (Active signals) |
| **ACTIVE** | Position being monitored | 0 (Active signals) |
| **TARGET_HIT** | Profit target reached | 29 |
| **STOP_LOSS** | Loss limit reached | 20 |
| **TIMEOUT** | Holding period exceeded | 1 |
| **EXPIRED** | Signal validity window closed | 0 |
| **CANCELLED** | Manual/System cancellation | 0 |

## 2. Trigger Logic Verification
- **LONG (Pullback)**: Triggered when `Low <= Entry`. Current 33 signals are correctly waiting as current price is above entry.
- **SHORT (Retracement)**: Triggered when `High >= Entry`. Current signals are correctly waiting as current price is below entry.

## 3. Freshness & Refresh
- **Background Worker**: Verified running every 5 minutes.
- **Current Price**: Fetched from institutional providers (NSE Open, Upstox, Dhan).
- **Staleness Gate**: 120h Freshness limit enforced.

---
**Verdict**: **PASS**
Lifecycle logic is causal, sound, and accurately reflects the frozen V2.2 methodology.
