# TradeMind AI — Feature Catalog V3

---

## 1. Feature Family Taxonomy

Features in TradeMindAI are grouped into 8 orthogonal feature families to minimize redundancy and maximize out-of-sample predictive power.

### Family 1: Trend & Momentum
- `EMA_20`, `EMA_50`, `EMA_200`: Exponential moving averages on 5m, 15m, 1D.
- `RSI_14`: Relative Strength Index (14 periods).
- `MACD_12_26_9`: Moving Average Convergence Divergence line and histogram.
- `ADX_14`: Average Directional Index measuring trend strength.

### Family 2: Volatility & Risk Geometry
- `ATR_14`: 14-period Average True Range.
- `NATR_14`: Normalized ATR percentage.
- `BOLLINGER_WIDTH`: Band width percentile.

### Family 3: Market Microstructure & Order Flow
- `OIB`: Top-5 Bid-Ask Order Book Imbalance ratio.
- `VPIN`: Volume-Synchronized Probability of Toxicity.
- `CVD`: Cumulative Volume Delta pressure.

### Family 4: Options & Derivatives
- `OPTIONS_PCR_OI`: Put-Call Ratio on Open Interest.
- `NET_DEALER_GEX`: Dealer Gamma Exposure.
- `MAX_PAIN_SHIFT`: Strike shift vector towards minimum seller loss.

### Family 5: Sector & Cross-Sectional Ranks
- `CROSS_SECTIONAL_MOMENTUM_RANK`: NIFTY-200 percentile rank.
- `SECTOR_RRG_QUADRANT`: Relative Rotation Graph quadrant (Leading, Improving, Weakening, Lagging).

### Family 6: Regime & Entropy
- `GAUSSIAN_HMM_STATE`: 3-State Hidden Markov Model.
- `TSALLIS_ENTROPY`: Non-extensive entropy index ($q=1.5$).

### Family 7: Macro & Sentiment
- `FINBERT_SENTIMENT`: Transformer-based filing sentiment.
- `JOHANSEN_COINTEGRATION`: USD/INR & Brent Crude Cointegration score.

### Family 8: AI Swarm & Telemetry
- `SWARM_CONSENSUS_SCORE`: 4-Agent Unanimity ratio ($1.00 = 4/4$).
- `PRICE_FEED_CONSENSUS`: 3-source price feed median consensus score.
