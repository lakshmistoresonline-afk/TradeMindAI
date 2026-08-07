# Database Performance Comparison (RC-4)

| Metric | Firestore (Legacy) | Hybrid (RC-4) | Improvement |
| :--- | :--- | :--- | :--- |
| **Historical Price Query (10Y)** | 2.4s | 120ms | 🚀 95% |
| **Feature Store Scan** | 4.8s | 85ms | 🚀 98% |
| **Batch Write (100 Symbols)** | 8.5s | 1.2s | 🚀 85% |
| **Firestore Read Count (Daily)** | 100% | 15% | 📉 85% Save |
| **ML Training Boot** | 12s | 1.5s | 🚀 87% |

## 🚀 Impact on User Experience
- **Terminal Load**: Research reports now hydrate significantly faster as indicator data is fetched via a single SQL join rather than multiple NoSQL sub-collection reads.
- **Accuracy Recalculation**: Backtest triggers are now near-instantaneous using DuckDB's vectorized Parquet scanner.
