# Step 4.5.23: First Live Shadow Signal Integrity & Lifecycle Report

**Date:** 2026-08-24
**Market Status:** OPEN
**Authoritative Source:** Neon PostgreSQL (Verified)
**Strategy:** V2.2 FROZEN

## 1. Data Classification Reconciliation
The NIFTY 200 universe results for the session start have been mathematically reconciled.

| Category | Count | Definition |
| :--- | :--- | :--- |
| **Total Universe** | 200 | Total constituents in NIFTY 200 canonical list. |
| **Operational** | 198 | Constituents with valid champion models and metadata. |
| **Unavailable** | 2 | GUJGASLTD, LTIM (Missing models/historical depth). |
| **Fresh Data** | 198 | Symbols where price/features were updated successfully today. |
| **Stale Data** | 0 | Symbols with data older than 24h (after DuckDB refresh). |
| **Liquidity Rejected** | 163 | Operational symbols with < 10M average daily volume. |
| **Candidates** | 35 | Symbols passing liquidity and preliminary technical filters. |
| **Valid Signals** | **18** | Symbols passing the complete Strategy V2.2 ensemble rules. |

## 2. Signal Integrity Verification (Total: 18)
All 18 newly generated signals have been verified in the authoritative Neon database.

| Signal ID | Symbol | Dir | Entry | Target | Stop | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| sig_ABB_202608240938 | ABB | LONG | 7503.0 | 7728.09 | 7277.91 | ACTIVE |
| sig_APOLLOHOSP_202608240938 | APOLLOHOSP | LONG | 8650.0 | 8909.5 | 8390.5 | ACTIVE |
| sig_ATGL_202608240938 | ATGL | SHORT | 643.75 | 624.44 | 663.06 | ACTIVE |
| sig_BAJAJHLDNG_202608240939 | BAJAJHLDNG | LONG | 11136.0 | 11470.08 | 10801.92 | ACTIVE |
| sig_BANKINDIA_202608240939 | BANKINDIA | SHORT | 141.11 | 136.88 | 145.34 | ACTIVE |
| sig_BATAINDIA_202608240939 | BATAINDIA | LONG | 692.25 | 713.02 | 671.48 | ACTIVE |
| sig_BERGEPAINT_202608240939 | BERGEPAINT | LONG | 516.35 | 531.84 | 500.86 | ACTIVE |
| sig_BIOCON_202608240939 | BIOCON | SHORT | 410.05 | 397.75 | 422.35 | ACTIVE |
| sig_BOSCHLTD_202608240939 | BOSCHLTD | LONG | 47995.0 | 49434.85 | 46555.15 | ACTIVE |
| sig_CANFINHOME_202608240939 | CANFINHOME | SHORT | 811.4 | 787.06 | 835.74 | ACTIVE |
| sig_COFORGE_202608240939 | COFORGE | LONG | 1875.6 | 1931.87 | 1819.33 | ACTIVE |
| sig_CUMMINSIND_202608241002 | CUMMINSIND | SHORT | 5164.5 | 5009.57 | 5319.44 | ACTIVE |
| sig_DIXON_202608241002 | DIXON | SHORT | 14530.0 | 14094.1 | 14965.9 | ACTIVE |
| sig_FORTIS_202608241002 | FORTIS | LONG | 915.25 | 942.71 | 887.79 | ACTIVE |
| sig_GLENMARK_202608241002 | GLENMARK | LONG | 2391.0 | 2462.73 | 2319.27 | ACTIVE |
| sig_INFY_202608241003 | INFY | LONG | 1169.20 | 1204.28 | 1134.12 | ACTIVE |
| sig_SBIN_202608241004 | SBIN | LONG | 1067.70 | 1099.73 | 1035.67 | ACTIVE |
| sig_WIPRO_202608241004 | WIPRO | LONG | 184.0 | 189.52 | 178.48 | ACTIVE |

## 3. Historical Preservation
The two previous historical Shadow records remain untouched and correct in the audit trail.
- `sig_SBIN_202608180715`: **TARGET_HIT** (Verified)
- `sig_SBIN_202608181011`: **TIMEOUT** (Verified)

## 4. Portfolio & Equity Reconciliation
- **Starting Equity:** ₹1,002,800
- **Realized P&L Today:** ₹0
- **Cumulative Realized P&L:** +₹2,800
- **Total Signal Count:** 20 (18 Today + 2 Historical)
- **Active Positions:** 18
- **Theoretical Allocation:** ₹100,000 per trade (10% Model)
- **Current Status:** Authoritative state synced across Neon and Firestore.

## 5. Deployment Integrity
- **Neon/Firestore Match:** PASS (18 new signals mirrored).
- **Dashboard Match:** PASS (18 Active Signals displayed).
- **Unique IDs:** PASS (Deterministic sig_SYMBOL_TIMESTAMP format).
- **No Artificial Data:** PASS (All signals derived from Strategy V2.2 inference).

---

**FINAL VERDICT:** STEP_4_5_23_FIRST_SHADOW_SIGNAL_INTEGRITY_VERIFIED
The first live shadow signals of the session are technically sound, persisted in the authoritative database, and correctly mirrored for public dashboard visibility.
