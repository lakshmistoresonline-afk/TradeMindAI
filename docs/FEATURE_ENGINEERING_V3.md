# TradeMind AI — Feature Engineering V3

---

## 1. Feature Transformation Pipeline

1. **Standardization & Scaling**: Robust Z-Score scaling based on 252-day rolling windows.
2. **Missing Value Handling**: Explicit quality flags (`MISSING`, `STALE`) rather than zero-filling.
3. **Outlier Winsorization**: 1st and 99th percentile winsorization on high-volatility features.
