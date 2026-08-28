# Step 4.5.32: Live Shadow Lifecycle & Reconciliation Report

**Date:** 2026-08-25
**Current IST:** 11:30 AM
**Market Status:** OPEN
**Session Status:** ACTIVE

## 1. Authoritative Signal Verification
A forensic audit of the Neon database confirmed the integrity of the 25 active shadow positions.

| Category | Count | Status |
| :--- | :--- | :--- |
| **Active Signals (Total)** | 25 | **VERIFIED** |
| **Carried Over (2026-08-24)** | 18 | **PRESERVED** |
| **New Signals (2026-08-25)** | 7 | **PERSISTED** |
| **Historical Signals (Terminal)**| 2 | **PRESERVED** |

### Signal ID Sample Audit
- `sig_ACC_202608250435`: ACTIVE
- `sig_BAJAJHLDNG_202608240939`: ACTIVE
- `sig_SBIN_202608241004`: ACTIVE

## 2. Lifecycle Evaluation Results
The current market prices were fetched for all 25 active symbols. No terminal conditions (Target Hit / Stop Loss) have been triggered since the session start.

| Status | Count | Detail |
| :--- | :--- | :--- |
| **TARGET_HIT** | 0 | No symbols reached +3.0% |
| **STOP_HIT** | 0 | No symbols reached -3.0% |
| **TIMEOUT** | 0 | No signals exceeded age limit |
| **ACTIVE** | 25 | Monitoring continues |

## 3. Data Count Reconciliation (NIFTY 200)
The variance between operational and refresh counts has been traced and explained.

| Metric | Count | Explanation |
| :--- | :--- | :--- |
| **Total Universe** | 200 | Canonical NIFTY 200 list. |
| **Operational** | 198 | Symbols with a verified champion model. |
| **Unavailable** | 2 | GUJGASLTD, LTIM (Missing models). |
| **Refresh Success** | 199 | Symbols with 2026-08-25 data in DuckDB. |
| **Refresh Failure** | 1 | LTIM (Data provider timeout). |

> [!NOTE]
> GUJGASLTD has successful data ingestion (199th symbol) but is not "Operational" because it lacks a champion model version for Strategy V2.2.

## 4. Layer Reconciliation Scorecard
| Field | Neon (Authoritative) | Firestore (Mirror) | API | Dashboard | Match |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Market Status | `OPEN` | `OPEN` | `OPEN` | `OPEN` | **YES** |
| Active Signals | 25 | 25 | 25 | 25 | **YES** |
| Total Equity | ₹1,002,800 | ₹1,002,800 | ₹1,002,800 | ₹1,002,800 | **YES** |
| Realized P&L | +₹2,800.00 | +₹2,800.00 | +₹2,800.00 | +₹2,800.00 | **YES** |

---

**FINAL VERDICT:** STEP_4_5_32_LIVE_SHADOW_MONITORING_ACTIVE
The system is fully reconciled. All 25 signals are accurately monitored using current market data. Performance optimizations from Step 4.5.21 are maintained.
