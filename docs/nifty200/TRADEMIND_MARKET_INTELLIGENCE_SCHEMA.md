# TRADEMIND AI: MARKET INTELLIGENCE SCHEMA

## 1. Market Regime
Captured at every evaluation cycle.
- **Regime**: BULL, BEAR, SIDEWAYS, VOLATILE, TRANSITION
- **Risk Mode**: RISK_ON, RISK_OFF, HEDGE, DELEVERAGE
- **Sentiment Score**: 0.0 to 1.0 (Composite of Trend, Breadth, VIX)
- **Volatility (VIX)**: India VIX absolute value

## 2. Institutional Intelligence
- **FII/DII Net**: Daily buy/sell flow in Crores.
- **Institutional Pressure**: Directional force (-1.0 to 1.0) derived from flow magnitude.
- **Cumulative Bias**: 10-day rolling sentiment trend.

## 3. Sector Rotation
- **Relative Strength**: Sector performance vs NIFTY 50.
- **Momentum**: 5-day rate of change.
- **Rank**: Ordered list of 10 primary NSE sectors.
- **State**: STRONGEST, IMPROVING, DETERIORATING, WEAKEST.
