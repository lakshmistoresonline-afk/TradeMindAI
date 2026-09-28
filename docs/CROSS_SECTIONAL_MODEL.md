# TradeMind AI — NIFTY 200 Cross-Sectional Ranking Model

---

## 1. Cross-Sectional Ranking Overview

Every stock in the NIFTY 200 universe is ranked cross-sectionally relative to its peers across 6 quantitative factors:

1. **Momentum Percentile**: 5d, 20d, 60d, 120d, 252d return percentile.
2. **Trend Percentile**: Distance from EMA20, EMA50, and EMA200.
3. **Relative Strength RRG**: Residual alpha vs. NIFTY 50 benchmark.
4. **Volume Acceleration**: Relative volume ($\text{Vol} / \text{Vol}_{20\text{d}}$) and turnover percentile.
5. **Volatility Expansion**: ATR expansion and Bollinger width percentile.
6. **Institutional Delivery**: Delivery volume acceleration and futures OI buildup.

---

## 2. Composite Score

$$\text{Composite Score} = 0.30 \times \text{Momentum} + 0.25 \times \text{Trend} + 0.20 \times \text{RS} + 0.15 \times \text{Volume} + 0.10 \times \text{Volatility}$$

Signals are prioritized based on Precision@K rankings within the top $10\%$ of the NIFTY 200 universe.
