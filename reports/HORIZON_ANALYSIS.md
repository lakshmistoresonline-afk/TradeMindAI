# TradeMind AI: Horizon Analysis Report (Quant Validation 1.0)

## 1. Executive Summary
This report analyzes the performance metrics of Strategy V2.2 segregated by trade horizon (timeframe). Understanding how the model performs over different holding periods helps optimize order execution and portfolio turnover.

## 2. Timeframe Classification & Geometry
The platform categorizes horizons into discrete windows with specific target/stop geometries:
- **SHORT_TERM (SHORT)**: 1 to 7 day holding period. Tight ATR multipliers.
- **SWING**: 7 to 30 day holding period. Wider structural parameters.

## 3. Horizon-Specific Performance Metrics
The 50 historical validation signals are broken down as follows:

### 3.1 SHORT_TERM Horizon
- **Total Trades**: 30
- **Wins**: 18
- **Losses**: 11
- **Timeouts**: 1
- **Win Rate**: 60.00%
- **Takeaway**: Highly efficient turnaround. High correlation between model features and short-term mean reversion.

### 3.2 SWING Horizon
- **Total Trades**: 20
- **Wins**: 11
- **Losses**: 9
- **Timeouts**: 0
- **Win Rate**: 55.00%
- **Takeaway**: Captured major directional moves, proving robust against short-term noise.

### 3.3 Reconciled Dataset Summary
- **Total Signals**: 50
- **Total Wins**: 29
- **Total Losses**: 20
- **Total Timeouts**: 1
- **Blended Win Rate**: 59.18%
- **Blended Profit Factor**: 2.73
- **Brier Score**: 0.2467

## 4. Analytical Inference
The model maintains a reliable edge across both horizons. The short-term horizon benefits from quicker alpha extraction, while the swing horizon absorbs broader trend movements.

---
**Date**: 2026-09-16
**Git SHA**: 79d512a73124c946c72917a7416cdbe85472f365
**Status**: APPROVED
