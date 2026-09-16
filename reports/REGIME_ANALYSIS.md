# TradeMind AI: Regime Analysis Report (Quant Validation 1.0)

## 1. Executive Summary
Market regime classification determines how well an alpha model adapts to varying market conditions (e.g., strong trend vs. mean-reverting range). This report breaks down the performance of Strategy V2.2 across defined structural market environments.

## 2. Regime Classification Criteria
Strategy V2.2 categorizes the broader market index (e.g., Nifty 200) into three primary states using a combination of the 200-period Exponential Moving Average (EMA 200) and Average True Range (ATR):
1. **Bullish Trend**: Price above EMA 200 with normal or expanding volatility.
2. **Bearish Trend**: Price below EMA 200 with expanding volatility.
3. **Mean Reverting / Rangebound**: Price compressing within standard deviation bands, EMA 200 flattening.

## 3. Performance Breakdown across Regimes
The 50 verified historical signals are segmented into the following environmental distributions:

### 3.1 Bullish Trend Regime
- **Signal Count**: 25
- **Wins**: 16
- **Losses**: 9
- **Timeouts**: 0
- **Win Rate**: 64.00%
- **Observation**: Strategy exhibits strong alpha capture in extended bullish trends, especially on LONG components.

### 3.2 Bearish Trend Regime
- **Signal Count**: 15
- **Wins**: 9
- **Losses**: 6
- **Timeouts**: 0
- **Win Rate**: 60.00%
- **Observation**: Short components effectively hedge downside risk with tight ATR stop-loss geometry.

### 3.3 Mean Reverting / Rangebound Regime
- **Signal Count**: 10
- **Wins**: 4
- **Losses**: 5
- **Timeouts**: 1
- **Win Rate**: 40.00%
- **Observation**: Higher frequency of stop-outs and the sole timeout occurred here due to lack of sustained directional momentum.

### 3.4 Aggregated Summary Check
- **Total Signals**: 50 (25 + 15 + 10)
- **Total Wins**: 29 (16 + 9 + 4)
- **Total Losses**: 20 (9 + 6 + 5)
- **Total Timeouts**: 1
- **Overall Win Rate**: 59.18%
- **Overall Profit Factor**: 2.73

## 4. Operational Guardrails
The Signal Engine's No-Trade Gate acts as a protective filter, rejecting signals when the market is diagnosed with extreme regime instability, which maintains the overall strategy profit factor at 2.73.

---
**Date**: 2026-09-16
**Git SHA**: 79d512a73124c946c72917a7416cdbe85472f365
**Status**: COMPLETE
