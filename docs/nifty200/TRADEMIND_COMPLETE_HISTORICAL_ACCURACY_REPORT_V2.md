# TRADEMIND AI: COMPLETE HISTORICAL ACCURACY REPORT (V2)

**Audit Timestamp**: 2026-09-04 12:17:29 UTC
**Total Historical Calls**: 1,259
**Forensically Verified**: 50 (4.0%)
**Current Verification Level**: LEVEL 4 (EXECUTION_VERIFIED) for Shadow sample.

## 1. Executive Summary
TradeMind AI has established a reproducible, independently audited shadow-validation pipeline for Strategy V2.2. In the current 50-observation verified sample, the system recorded a **58.0% win rate** and **2.72 profit factor**. These results are promising but remain sample-limited and are not yet statistically significant at the conventional 5% threshold.

## 2. Population Reconciliation
| Classification | Record Count | % of Total | Truth Status |
| :--- | :--- | :--- | :--- |
| **REAL_LIVE_SHADOW** | 50 | 4.0% | **VERIFIED** |
| **ACTIVE_SHADOW** | 14 | 1.1% | **MONITORING** |
| **UNVERIFIED_HISTORICAL**| 1,195 | 94.9% | UNVERIFIED |
| **TOTAL UNIQUE CALLS** | **1,259** | 100% | |

## 3. Authoritative Performance (n=50 Verified)
| Metric | Value | Institutional Interpretation |
| :--- | :--- | :--- |
| **Call Accuracy (WR)** | 58.00% | **PROMISING** |
| **Profit Factor** | 2.72 | **POSITIVE — SAMPLE LIMITED** |
| **Total Net P&L** | +126.75% | Observed Accumulation |
| **Expectancy** | +2.535% | Observed Net Edge |
| **Trade Seq Drawdown** | 15.69% | Reconciled |

## 4. Integrity Verification
- **Look-ahead Guard**: **PASS**. 100% temporal isolation confirmed.
- **Zero Fabrication**: **PASS**. 50/50 outcomes verified against 1m OHLC terminal hits.
- **P&L Reconciliation**: **PASS**. Friction-aware canonical engine active.

---
**Status**: `TRADEMIND_50_OF_50_VALIDATION_CERTIFIED`
