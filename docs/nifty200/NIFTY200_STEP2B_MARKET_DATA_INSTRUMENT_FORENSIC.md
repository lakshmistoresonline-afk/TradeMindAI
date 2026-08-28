# NIFTY 200 Step 2B — Forensic Market Data & Instrument Report (P0)

## 1. Complete 11-Signal Forensic Baseline

| # | SIGNAL ID | SYMBOL | TYPE | INSTRUMENT ID | DIR | CREATED | DATA TS | ENTRY | TARGET | STOP | CURRENT* | PROB | EV | R:R | STATUS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | master_eq_INFY_122636 | INFY | EQUITY | INFY | LONG | 12:26:36 | 12:26:06 | 1910.0 | 2050.0 | 1860.0 | 1109.5 | 0.80 | 102.2 | 2.8 | ACTIVE |
| 2 | master_eq_ITC_122636 | ITC | EQUITY | ITC | LONG | 12:26:36 | 12:26:06 | 495.0 | 550.0 | 482.0 | 268.5 | 0.75 | 37.9 | 4.23 | ACTIVE |
| 3 | master_eq_LT_122636 | LT | EQUITY | LT | LONG | 12:26:36 | 12:26:06 | 3550.0 | 3850.0 | 3480.0 | 4051.3 | 0.85 | 242.7 | 4.29 | ACTIVE |
| 4 | master_eq_RELIANCE_122636 | RELIANCE | EQUITY | RELIANCE | LONG | 12:26:36 | 12:26:06 | 2980.0 | 3150.0 | 2920.0 | 1291.1 | 0.83 | 131.1 | 2.83 | ACTIVE |
| 5 | master_eq_TCS_122636 | TCS | EQUITY | TCS | LONG | 12:26:36 | 12:26:06 | 4520.0 | 4800.0 | 4450.0 | 2252.8 | 0.78 | 201.6 | 4.0 | ACTIVE |
| 6 | master_fut_BANKNIFTY_122636 | BANKNIFTY | FUTURES | BANKNIFTY FUT | LONG | 12:26:36 | 12:26:06 | 52600.0 | 53800.0 | 52100.0 | 57585.1 | 0.73 | 741.0 | 2.4 | ACTIVE |
| 7 | master_fut_NIFTY_122636 | NIFTY | FUTURES | NIFTY FUT | LONG | 12:26:36 | 12:26:06 | 24850.0 | 25200.0 | 24650.0 | 24131.7 | 0.76 | 214.7 | 1.75 | ACTIVE |
| 8 | master_fut_RELIANCE_122636 | RELIANCE | FUTURES | RELIANCE FUT | LONG | 12:26:36 | 12:26:06 | 3010.0 | 3180.0 | 2960.0 | 1291.1 | 0.78 | 120.9 | 3.4 | ACTIVE |
| 9 | master_opt_NIFTY_25000_122636 | NIFTY | OPTIONS | NIFTY 25000.0 CE | LONG | 12:26:36 | 12:26:06 | 155.0 | 280.0 | 95.0 | 24132.4 | 0.79 | 86.3 | 2.08 | ACTIVE |
| 10 | master_opt_RELIANCE_3100_122636 | RELIANCE | OPTIONS | RELIANCE 3100.0 CE | LONG | 12:26:36 | 12:26:06 | 48.0 | 95.0 | 30.0 | 1291.0 | 0.76 | 31.2 | 2.61 | ACTIVE |
| 11 | master_opt_SBIN_860_122636 | SBIN | OPTIONS | SBIN 860.0 CE | LONG | 12:26:36 | 12:26:06 | 18.0 | 42.0 | 10.0 | 1043.7 | 0.67 | 13.2 | 3.0 | ACTIVE |

\* *Note: Current price for Derivatives is currently mapping to the Underlying Index/Spot price (Confirmed Defect).*

## 2. Market Data Freshness (Full 200 Universe)
- **Universe Records**: 210
- **Latency Statistics (Seconds)**:
  - Minimum: 8599.8s
  - Maximum: 961922.5s
  - Average: 54026.6s
  - Median:  8634.4s
  - P95:     8665.5s
- **Status Classification**:
  - **FRESH**: 0
  - **STALE (>1h)**: 210
  - **MISSING**: 0

## 3. Forensic Investigation Findings

### **Anomaly 1: Equity Price Mismatch (Corporate Actions)**
- **Finding**: Large discrepancies in INFY, ITC, RELIANCE, TCS.
- **Cause**: Hardcoded master baseline signals use **Unadjusted Historical Prices** (Pre-Bonus/Pre-Split), while the live provider returns **Current Adjusted Prices**.
- **Evidence**: RELIANCE Entry 2980.0 (Unadjusted) vs Live 1290.9 (Adjusted/Post-Bonus).
- **Status**: **IDENTIFIED (Baseline vs Live Mismatch)**

### **Anomaly 2: Derivative Mapping Bug**
- **Finding**: Options/Futures Current Price = Underlying Price.
- **Cause**: `YFinanceProvider.get_ltp(symbol)` uses the `symbol` field which defaults to underlying ticker mapping (e.g. NIFTY -> ^NSEI).
- **Status**: **BUG CONFIRMED (Mapping requires Instrument Context)**

### **Anomaly 3: Look-Ahead Bias Audit**
- **Verification**: `Market Data Timestamp (12:26:06) < Signal Created At (12:26:36)`.
- **Result**: ✅ **PASS**. All indicators were calculated from T-minus snapshots.

## 4. Cross-Platform Reconciliation
- **Neon Authority**: Matches audit table exactly.
- **API (v1/ios/signals/live)**: confirmed returning all 11 master nodes.
- **Dashboard**: Verified rendering.
- **F&O Coverage**: **PARTIAL** (7 seeded contracts).

## 5. Final Status
**STATUS: NIFTY200_STEP2B_CURRENT_PRICE_MAPPING_FAILURE**
*Reason: Derivative current prices are incorrectly mapping to underlying spot values.*
