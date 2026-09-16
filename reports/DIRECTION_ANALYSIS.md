# TradeMind AI: Direction Analysis Report (Quant Validation 1.0)

## 1. Executive Summary
This report analyzes performance variation based on trade direction (LONG vs. SHORT). Ensuring symmetrical alpha capture or understanding directional skew is essential for risk allocation and portfolio sizing controls.

## 2. Directional Performance Slicing
The 50 historical signals used for Strategy V2.2 validation are divided into LONG and SHORT categories:

### 2.1 LONG Signals
- **Total Trades**: 22
- **Wins (Target Hit)**: 14
- **Losses (Stop Loss)**: 8
- **Timeouts**: 0
- **Win Rate**: 63.64%
- **Characteristics**: LONG signals show slightly higher win rates, aligning well with broader market upward drift.

### 2.2 SHORT Signals
- **Total Trades**: 28
- **Wins (Target Hit)**: 15
- **Losses (Stop Loss)**: 12
- **Timeouts**: 1
- **Win Rate**: 53.57%
- **Characteristics**: SHORT signals show higher volume due to the mid-September downside market correction, with the sole timeout occurring on a short position that consolidated.

### 2.3 Consolidated Totals
- **Total Signals**: 50
- **Total Wins**: 29
- **Total Losses**: 20
- **Total Timeouts**: 1
- **Blended Win Rate**: 59.18%
- **Blended Profit Factor**: 2.73

## 3. Risk & Sizing Controls
The Risk Engine applies symmetrical 2% fixed fractional risk across both directions, ensuring that short-side volatility does not disproportionately damage equity curve metrics.

---
**Date**: 2026-09-16
**Git SHA**: 79d512a73124c946c72917a7416cdbe85472f365
**Real Trading**: FALSE
