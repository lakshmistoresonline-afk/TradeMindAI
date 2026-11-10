# TradeMindAI — Phase B Canonical Indicator Formulas & Specification

**Authoritative Module**: [backend/app/services/indicator_service.py](file:///D:/TradeMindAI/backend/app/services/indicator_service.py)

---

## 1. Indicator Mathematical Definitions

### 1. Relative Strength Index (Wilder RSI 14)
- **Delta**: $D_t = \text{Close}_t - \text{Close}_{t-1}$
- **Gain**: $G_t = \max(D_t, 0)$, **Loss**: $L_t = \max(-D_t, 0)$
- **Initial Smoothing (Bar 14)**:
  $$\text{AvgGain}_{14} = \frac{1}{14} \sum_{i=1}^{14} G_i, \quad \text{AvgLoss}_{14} = \frac{1}{14} \sum_{i=1}^{14} L_i$$
- **Wilder Exponential Smoothing (Bar $t > 14$)**:
  $$\text{AvgGain}_t = \frac{\text{AvgGain}_{t-1} \times 13 + G_t}{14}, \quad \text{AvgLoss}_t = \frac{\text{AvgLoss}_{t-1} \times 13 + L_t}{14}$$
- **RSI Calculation**:
  $$\text{RSI}_t = 100 - \frac{100}{1 + \frac{\text{AvgGain}_t}{\text{AvgLoss}_t}}$$
- **Edge-Case Rules**:
  - $L_t = 0, G_t > 0 \implies \text{RSI} = 100.0$
  - $G_t = 0, L_t > 0 \implies \text{RSI} = 0.0$
  - $G_t = 0, L_t = 0 \implies \text{RSI} = 50.0$
  - $t < 14 \implies \text{RSI} = \text{NaN}$

---

### 2. Exponential Moving Averages (EMA $N$)
- **Multiplier**: $K = \frac{2}{N + 1}$
- **Recurrence Relation**:
  $$\text{EMA}_t = (\text{Close}_t \times K) + (\text{EMA}_{t-1} \times (1 - K))$$
- **Warm-Up Guard**:
  - EMA 20: Requires $\ge 20$ bars.
  - EMA 50: Requires $\ge 50$ bars.
  - EMA 100: Requires $\ge 100$ bars.
  - EMA 200: Requires $\ge 200$ bars (returns `NaN` if $\text{bars} < 200$).

---

### 3. Moving Average Convergence Divergence (MACD 12, 26, 9)
- **MACD Line**: $\text{MACD}_t = \text{EMA}_{12}(\text{Close}_t) - \text{EMA}_{26}(\text{Close}_t)$
- **Signal Line**: $\text{Signal}_t = \text{EMA}_9(\text{MACD}_t)$
- **Histogram**: $\text{Hist}_t = \text{MACD}_t - \text{Signal}_t$
- **Warm-Up Guard**: Returns `NaN` if $\text{bars} < 26$.

---

### 4. Average True Range (ATR 14)
- **True Range**:
  $$\text{TR}_t = \max(\text{High}_t - \text{Low}_t, |\text{High}_t - \text{Close}_{t-1}|, |\text{Low}_t - \text{Close}_{t-1}|)$$
- **ATR 14**: Rolling 14-bar mean of $\text{TR}_t$.
- **Warm-Up Guard**: Returns `NaN` if $\text{bars} < 14$. No constant factor fallback ($0.02 \times \text{Price}$ is forbidden).

---

### 5. Bollinger Bands (20, 2.0)
- **Middle Band**: $\text{SMA}_{20}(\text{Close}_t)$
- **Upper Band**: $\text{SMA}_{20} + (2.0 \times \sigma_{20})$
- **Lower Band**: $\text{SMA}_{20} - (2.0 \times \sigma_{20})$
- **Warm-Up Guard**: Returns `NaN` if $\text{bars} < 20$.

---

### 6. Donchian Channels (20) — Point-in-Time Causality Shift
- **Donchian High**: $\max(\text{High}_{t-20 \dots t-1})$ (Shifted 1 bar: `high.rolling(20).max().shift(1)`)
- **Donchian Low**: $\min(\text{Low}_{t-20 \dots t-1})$ (Shifted 1 bar: `low.rolling(20).min().shift(1)`)
- **Causality Guard**: Shifting 1 bar ensures that bar $t$'s price action cannot leak into its own channel bounds. Returns `NaN` if $\text{bars} < 21$.
