# TRADEMIND AI: NIFTY 200 — CONTINUOUS SHADOW MONITORING REPORT

## 1. Executive Summary
Continuous LIVE_SHADOW observation is active. As of 2026-08-28, the system has successfully identified and verified 15 outcomes for Strategy V2.2. The accumulation phase is progressing steadily toward the 20-trade performance gate.

## 2. Signal Accumulation Progress
- **Total Shadow Signals**: 27
- **Active Signals**: 12
- **Verified Outcomes**: **15 / 20** (Milestone: 75%)
- **Remaining**: 5

## 3. Outcome Distribution (Verified)
| Outcome Type | Count | Percentage |
| :--- | :--- | :--- |
| **TARGET_HIT** | 7 | 46.7% |
| **STOP_LOSS** | 7 | 46.7% |
| **TIMEOUT** | 1 | 6.6% |
| **EXPIRED** | 0 | 0.0% |
| **CANCELLED** | 0 | 0.0% |

## 4. Performance Summary (Descriptive Only)
| Metric | Value |
| :--- | :--- |
| **Gross Realized P&L** | +1.4% (Across 15 units) |
| **Total Friction (Fees/Slippage)** | -3.0% (0.20% per trade) |
| **Net Realized P&L** | -1.6% |
| **Max Drawdown (Shadow)** | 3.2% |

*Note: These statistics are based on a small sample and are not statistically significant.*

## 5. Data Quality & Reliability
- **Market Data Freshness**: 95% (Occasional `STALE_MARKET_DATA` rejections during early session).
- **Instrument Mapping**: 100% (All 27 signals forensically linked to `instrument_id`).
- **Lifecycle Integrity**: **PASSED**. Irreversible state machine verified.
- **Provider Health**: Groww/YFinance switching operational.

## 6. Daily Reconciliation Audit
- **Neon vs API**: **MATCHED**.
- **Neon vs Firestore**: **MATCHED**.
- **Dashboard vs API**: **MATCHED**.

## 7. Discrepancy Tracking
- **Issue**: `NIFTY200_HISTORICAL_LIVE_SIGNAL_SYNC_DISCREPANCY`
- **Description**: Discrepancy in historical live signals (1232 vs 1089).
- **Impact**: Non-critical for shadow observation. Investigation pending.

## 8. Final Status
**NIFTY200_STEP4_PASS_PENDING_SAMPLE_SIZE**
Observation continues. Target: 20 verified outcomes.
