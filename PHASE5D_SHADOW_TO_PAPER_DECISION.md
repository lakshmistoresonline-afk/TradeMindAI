# PHASE 5D: SHADOW TO PAPER DECISION REPORT

## 1. Observation Summary
- **Period:** 2026-08-18 (Phase 5D Initiation)
- **Sessions Completed:** 1
- **Strategy:** `trademind-equity-v2.2` (FROZEN)
- **Current Sample Status:** **INSUFFICIENT_SAMPLE (0 / 20 Completed Trades)**

## 2. Universe & Model Coverage
| Category | Count | Status |
| :--- | :--- | :--- |
| NIFTY 200 Universe | 200 | 100% Monitored |
| Eligible Symbols | 196 | Models & Data Active |
| Blocked Symbols | 4 | LTIM, GUJGASLTD, PEL, TATAMOTORS |
| Model Success | 196/196 | Deterministic Inference |

## 3. Signal & Trade Distribution
- **Total Evaluations:** 200
- **Trade Signals Generated:** 1 (SBIN)
- **Signals Persisted to DB:** 1
- **Signals Resolved (Outcomes):** 0
- **No-Trade Decisions:** 199

## 4. No-Trade Rejection Analysis (Cumulative)
| Rejection Reason | Count | Logic Gate |
| :--- | :--- | :--- |
| INSUFFICIENT_LIQUIDITY | 187 | 10M Volume (Enforced) |
| TREND_CONFLICT | 4 | EMA-200 Filter (Enforced) |
| WEAK_EDGE | 2 | 0.52 Prob Threshold (Enforced) |
| STALE_MARKET_DATA | 2 | 24h Freshness (Enforced) |

## 5. Performance Monitoring
| Metric | Historical Baseline | Shadow Results |
| :--- | :--- | :--- |
| Win Rate | 58.77% | N/A |
| Net EV per Trade | 0.3262% | N/A |
| Mean Prob | 0.5870 | 0.5850 |
| Drift | 0.0000 | -0.0020 (STABLE) |

## 6. Data Integrity & Safety
- **Forensic Scan Status:** **SECURE**
- **Synthetic Data:** 0 detected.
- **Outcome Fabrication:** 0 detected.
- **Drawdown Circuit Breaker:** Active (Current DD: 0.00%)

## 7. Statistical Adequacy Assessment
- **Status:** **INSUFFICIENT**
- **Requirement:** $\ge 20$ completed trades.
- **Progress:** 0 / 20 (0.0%)

## 8. Final Decision & Recommendation
**CONTINUE_SHADOW**
The infrastructure is stable and integrity is 100% verified. The system is correctly enforcing all Strategy v2.2 safety gates. Advancement to Paper Trading is **HOLD** until the 20-trade milestone is achieved.

## Final Status
`SHADOW_HEALTHY_INSUFFICIENT_SAMPLE`
