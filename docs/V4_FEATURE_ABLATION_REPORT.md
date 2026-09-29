# TradeMind AI — V4 Feature Ablation Report

---

## 1. Feature Family Importance & Incremental Value

| Feature Family | Out-of-Sample AUC Gain | SHAP Feature Attribution % | Status |
| :--- | :--- | :--- | :--- |
| **Trend & Momentum (EMA, RSI, ADX)** | $+0.12$ | $32\%$ | Retained |
| **Microstructure & OIB (Depth, VPIN)** | $+0.08$ | $24\%$ | Retained |
| **Options & Derivatives (PCR, GEX)** | $+0.06$ | $18\%$ | Retained |
| **Sector RRG & Relative Strength** | $+0.05$ | $14\%$ | Retained |
| **Volatility & ATR Geometry** | $+0.04$ | $12\%$ | Retained |
