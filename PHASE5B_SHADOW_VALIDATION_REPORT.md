# PHASE 5B: SHADOW MODE VALIDATION REPORT

## 1. Execution Summary
- **Period:** 2026-08-18
- **Strategy:** `trademind-equity-v2.2` (FROZEN)
- **Objective:** Full-Universe Real Observation
- **Status:** **SHADOW_HEALTHY_INSUFFICIENT_SAMPLE**

## 2. Universe Coverage
| Category | Count | Status |
| :--- | :--- | :--- |
| NIFTY 200 Constituents | 200 | Primary Universe |
| Eligible for Strategy | 196 | Models & Data Verified |
| Blocked (Data Gaps) | 4 | LTIM, GUJGASLTD, PEL, TATAMOTORS |

## 3. Model Coverage
- **Certified v2.2 Models:** 196 (Exactly 11 features, RF Depth 5)
- **Successful Inferences:** 196 / 196
- **Deterministic Check:** PASSED (Verified via smoke test)

## 4. Data Freshness
- **Fresh ( < 24h):** 198 / 200
- **Stale:** 2 (BANDHANBNK, HUDCO)
- **Remediation:** Data sync was successful for 198 symbols; the 2 remaining stale symbols are handled by the safety gate.

## 5. Signal Generation
- **Total Trade Signals:** 1 (SBIN, LONG, Prob 0.629)
- **Total Rejections:** 199
- **Rejection Primary Cause:** `INSUFFICIENT_LIQUIDITY` (187) - NIFTY 200 includes mid-cap stocks that often fail the strict 10M volume gate.

## 6. Model Inference Quality
- **Numeric Probabilities:** ALL (0.0 to 1.0)
- **NaN / Inf Check:** PASSED
- **Runtime Error Rate:** 0.0%

## 7. Shadow Performance
- **Active Trades:** 1
- **Completed Trades:** 0
- **Net EV:** N/A (Insufficient sample)
- **Win Rate:** N/A

## 8. Drift Analysis
- **Current Prob Mean:** 0.578 (vs Certified 0.587)
- **Drift Status:** **NEGLIGIBLE**
- **Regime:** Bullish Momentum (Major indices near ATH)

## 9. Data Integrity
- **Forensic Check:** PASSED
- **Synthetic Data Usage:** NONE
- **Outcome Fabrication:** NONE

## 10. Safety Gates
- **Stale Gate (24h):** ENFORCED
- **Liquidity Gate (10M):** ENFORCED
- **EMA-200 Filter:** ENFORCED
- **Probability Filter (0.52):** ENFORCED

## 11. Statistical Sample Assessment
- **Status:** **INSUFFICIENT**
- **Recommendation:** Continue Shadow Mode for 5–10 trading sessions to accumulate a minimum of 20 completed observations before Paper Trading certification.

## 12. Shadow-to-Paper Recommendation
**HOLD** - Infrastructure is READY, but statistical performance needs a larger sample to verify the "Out-of-Sample" edge.

## Final Decision
`SHADOW_HEALTHY_INSUFFICIENT_SAMPLE`
