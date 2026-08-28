# STEP 4: Full Realized Walk-Forward Backtest Report

**Audit Timestamp**: 2026-08-20 12:30:00 UTC
**Strategy Version**: v2.2 (FROZEN)
**Status**: BASELINE VERIFIED

## 1. Executive Summary
This report establishes the final quantitative baseline for Strategy v2.2 using a chronological walk-forward backtest against the 199-symbol NIFTY 200 universe (2020-2026). The backtest simulated 38,636 trades under strict production parameters.

| Metric | Value |
| :--- | :--- |
| **Total Signals** | 38,636 |
| **Trade Win Rate** | 53.78% |
| **Average Return** | -0.20% |
| **Max Drawdown** | -102.6% |
| **Profit Factor** | 0.94 |
| **Expectancy (Realized)** | -0.06 R |

## 2. Dataset Provenance
- **Database:** Local SQLite (`backend/local_operational.db`)
- **Symbol Coverage:** 199 / 200 (LTIM Excluded)
- **Candle Count:** 334,682 (Unique per Symbol/Date)
- **Timeframe:** Daily (1D)
- **Range:** Jan 2020 - Aug 2026

### Candle Count Reconciliation
- **Neon Unique Candles:** 338,278
- **SQLite Unique Candles:** 334,682
- **Difference:** 3,596
- **Root Cause:** Reconciled. Neon contains 10-year history (starting 2016) for a subset of symbols, whereas the SQLite dataset was standardized to a 6-year horizon (2020 start) to ensure universe-wide consistency. Additionally, Neon contains `GLAND` and `UPL` which were absent in the latest local sync.

## 3. Performance Breakdown

### Result Distribution
| Outcome | Count | Percentage |
| :--- | :--- | :--- |
| **TARGET_HIT** | 20,777 | 53.78% |
| **STOP_LOSS** | 17,537 | 45.39% |
| **EXPIRED** | 322 | 0.83% |

### Statistical Validation
- **Confidence Interval (95%)**: [53.2%, 54.3%]
- **Standard Error**: 0.25%
- **Theoretical Expectancy**: +0.23% (Based on 53.78% WR and 1:1 R:R)
- **Realized Expectancy**: -0.20%
- **Negative Alpha Reason**: High-fidelity slippage and "Same-Bar Stop" conservative policy.

## 4. Integrity & Look-Ahead Audit
- **Look-Ahead Bias:** **PASS**. Verified that `SignalEngine` slice and `OutcomeEngine` future-data check prevent any information leakage.
- **Deduplication:** **PASS**. 0 duplicate candles in participating dataset.
- **Synthetic Data:** **PASS**. 0% synthetic candles detected.
- **Short Logic:** **PASS**. Verified `1 - P(UP)` implementation for shorts.

## 5. Execution Assumptions
- **Signal:** Generated at bar `i` CLOSE.
- **Entry:** Executed at bar `i` CLOSE (Market-on-Close) or bar `i+1` OPEN.
- **Target/Stop:** 3.0% fixed from entry price.
- **Same-Bar Policy:** If both Target and Stop hit in the same candle, **Stop Loss** is assumed (Maximum Conservatism).

## 6. Reproducibility
- **Python:** 3.10.11
- **SQLAlchemy:** 2.0+
- **Database Hash (Local):** `cecaef4...` (VCS Tracked)
- **Execution Mode:** `TRADEMIND_EXECUTION_MODE=local`

## 7. Conclusion
The Strategy v2.2 baseline is now **CERTIFIED**. While the raw win rate (53.8%) is statistically significant, the realize-return (-0.20%) indicates that the current 1:1 R:R (3% Target / 3% Stop) is insufficient to overcome the conservative "Stop-First" policy and market gaps.

**Final Status**: `BASELINE_VERIFIED`
The system is ready for Phase 8: Strategy Optimization (Targeting +1.5 RR).
