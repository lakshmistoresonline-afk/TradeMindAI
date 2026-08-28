# Firestore Usage Policy (RC-4)

## 🎯 Retained Datasets
Following the hybrid migration, Firestore is reserved strictly for **user-centric, real-time, and high-interactivity data**.

| Collection | Data Type | Usage |
| :--- | :--- | :--- |
| `users` | USER | Authentication and profile metadata. |
| `watchlists` | USER | Real-time watchlist synchronization. |
| `portfolio_health`| USER | Dashboard snapshots of portfolio audit. |
| `research_notes` | USER | Collaborative terminal annotations. |
| `trade_journal` | USER | Execution history and AI coaching feedback. |
| `strategies` | USER | Private user-defined trading rules. |
| `workspaces` | USER | UI layout and terminal state persistence. |
| `devices` | SYSTEM | FCM tokens and push notification routing. |
| `feature_definitions`| SYSTEM | Small volume metadata for the feature store mapping. |

## 🚫 Migrated Datasets (Removed from Firestore)
- `stocks/prices` (Sub-collection) -> **PostgreSQL**
- `feature_store` -> **DuckDB / Parquet**
- `market_regimes` -> **PostgreSQL**
- `intel_reports` -> **PostgreSQL**
- `predictions` -> **PostgreSQL**

## 📉 Optimization Metrics
- **Firestore Reads**: Target 85% reduction.
- **Firestore Writes**: Target 90% reduction (Large batches moved to SQL).
- **Cost**: Stay within Spark Plan limits for up to 10,000 users.
