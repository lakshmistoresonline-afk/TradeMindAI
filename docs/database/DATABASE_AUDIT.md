# TradeMind AI DATABASE AUDIT (Firestore)

## 📊 Firestore Collection Inventory

| Collection | Purpose | Category | Volume | Growth |
| :--- | :--- | :--- | :--- | :--- |
| `stocks` | Stock metadata & AI consensus | MARKET DATA | 100 docs | Stable |
| `stocks/{symbol}/prices` | Time-series OHLCV & Indicators | MARKET DATA | High (10Y/stock) | Linear |
| `news` | Market News Articles | MARKET DATA | Medium | Linear |
| `institutional_flow` | FII/DII Net Flow Data | MARKET DATA | Daily docs | Linear |
| `feature_store` | ML input vectors | ANALYTICAL DATA | High | Linear |
| `predictions` | AI/ML output history | ML DATA | High | Linear |
| `portfolio_health` | User portfolio audit snapshots | USER DATA | 1 per user | Low |
| `alerts` | User notification history | USER DATA | High | Linear |
| `earnings` | Corporate earnings data | MARKET DATA | 4 per symbol/year | Stable |
| `options_chains` | Derivatives data snapshots | MARKET DATA | High | Rapid |
| `model_registry` | ML model metadata & versions | SYSTEM DATA | Low | Low |
| `ml_datasets` | Training dataset metadata | ANALYTICAL DATA | Low | Low |
| `devices` | FCM tokens and device info | SYSTEM DATA | 1 per device | Low |
| `feature_definitions` | DNA mapping for feature store | SYSTEM DATA | ~50 docs | Stable |
| `strategies` | User-defined trading rules | USER DATA | 1-5 per user | Low |
| `paper_orders` | Executed virtual trades | USER DATA | High | Linear |
| `virtual_portfolios` | Paper trading accounts | USER DATA | 1 per user | Low |
| `workspaces` | Terminal layout preferences | USER DATA | 1-3 per user | Low |
| `research_notes` | User terminal annotations | USER DATA | Medium | Linear |
| `market_regimes` | Market phase history (Bull/Bear) | MARKET DATA | Daily docs | Linear |
| `opportunities` | AI-detected breakouts/reversals | MARKET DATA | 10-20 daily | Linear |
| `intel_reports` | Session summaries (Daily Briefs) | MARKET DATA | Daily docs | Linear |
| `trade_journal` | Post-trade audit & AI coaching | USER DATA | High | Linear |
| `backtests` | Strategy performance audits | ANALYTICAL DATA | 1 per symbol | Stable |

## 🔍 Critical Bottlenecks Identified
- **Price History**: Storing 10 years of OHLCV in Firestore sub-collections is costly and inefficient for range queries.
- **Feature Store**: High-frequency writes of analytical vectors to Firestore hits Spark Plan limits quickly.
- **Options Chains**: Large document sizes and high update frequency are not suitable for NoSQL.
- **Analytics**: Backtesting and ML training require scanning large ranges, which is expensive in Firestore (Read per document).
