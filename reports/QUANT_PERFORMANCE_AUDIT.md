# TradeMind AI: Quantitative Performance Audit (Quant Validation 1.0)

## Executive Summary
This audit provides a terminal recalculation of all key performance metrics for Strategy V2.2 based on a verified population of 49 historical signals.

## 1. Terminal Metrics
| Metric | Value |
| :--- | :--- |
| **Sample Size** | 49 |
| **Wins (Target Hit)** | 29 |
| **Losses (Stop Loss)** | 20 |
| **Win Rate** | **59.18%** |
| **Profit Factor** | **2.73** |
| **Expectancy** | **2.5908** |
| **Net P&L (Aggregate %)** | **+126.95%** |
| **Max Drawdown** | **-19.28%** |

## 2. P&L Forensics
- **Friction Model**: Recalculated using the canonical P&L Engine (0.20% friction applied to all trades).
- **Outlier Sensitivity**:
    - Net P&L (Full): +126.95%
    - Without Top 3 Trades: +97.55%
    - Without Bottom 3 Trades: +139.55%
- **Expectancy Robustness**: The positive expectancy of 2.59% per trade is an observed statistical edge in the current sample, exceeding the minimum threshold of 0.5% for production baseline.

## 3. Segmented Performance
### 3.1 By Direction
- **LONG**: 35 trades, Mean P&L: +2.82%, Total P&L: +98.69%
- **SHORT**: 14 trades, Mean P&L: +2.02%, Total P&L: +28.26%
- *Conclusion*: Strategy shows strong long bias efficiency but remains profitable in short scenarios.

### 3.2 By Regime
- **BULLISH**: 22 trades, Mean P&L: -0.21% (Caution)
- **SIDEWAYS**: 1 trade, Mean P&L: +2.80%
- **MISSING DATA**: 26 trades (Critical finding - 53% of historical signals lack regime metadata).

## 4. Conclusion
Strategy V2.2 meets the core performance criteria for production stability. However, the missing market regime metadata for >50% of the historical population indicates a need for better logging in future iterations, though it does not invalidate the realized P&L.

---
**Audit Date**: 2026-09-16
**Status**: PASS (With Metadata Warning)
