# TradeMind AI — Labeling Methodology

---

## 1. Triple-Barrier Labeling Framework

TradeMindAI uses a **Triple-Barrier Labeling Framework** for model training:

1. **Upper Barrier**: $\text{Entry} + (2.8 \times \text{ATR}_{14})$ $\rightarrow$ Label $+1$ (Target Hit).
2. **Lower Barrier**: $\text{Entry} - (2.0 \times \text{ATR}_{14})$ $\rightarrow$ Label $-1$ (Invalidated).
3. **Time Barrier**: 30 Trading Days $\rightarrow$ Label $0$ (Timeout / Expired).
