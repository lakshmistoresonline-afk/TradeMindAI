# TradeMind AI: Production Architecture Documentation

## 1. System Overview
TradeMind AI is a high-fidelity algorithmic trading platform designed for the NIFTY 200 universe. It operates in a hardened shadow mode to validate predictive alpha before capital deployment.

## 2. Data Flow
### Market Data Tier
- **Ingestion**: 1m and Daily OHLCV data from multi-provider source (Yahoo Finance / Groww).
- **Data Quality**: Centralized `DataQualityService` validates candles for future-dated timestamps and logical OHLC integrity.

### Intelligence Tier
- **Feature Store**: Persists technical and institutional features in an analytical DuckDB engine.
- **Model Registry**: Formal tracking of Random Forest champion models with versioning and metrics.
- **Prediction Ledger**: Every model inference is persisted in the `predictions` table, capturing directional probability and expected value (EV) at T0.

### Signal Tier
- **Signal Engine**: Generates immutable signals linked to specific `prediction_id`s.
- **Audit Trail**: Every state transition (`GENERATED` -> `ACTIVE` -> `TERMINAL`) is logged in the `shadow_events` table for forensic audit.

### Execution & Lifecycle
- **Outcome Engine**: Forensically audits terminal hits (High/Low/Open) to ensure execution accuracy.
- **Cost Model**: Enforces a 0.20% round-trip friction model (Fees + Slippage).

## 3. Portfolio & Accounting
- **Shadow Portfolio Engine**: Tracks virtual capital (₹10L) with real-time mark-to-market.
- **Exposure Management**: Monitors sector concentration and LONG/SHORT directional asymmetry.
- **Daily Snapshots**: Automated EOD preservation of equity curves and performance metrics.

## 4. Integrity & Safety
- **Master Authority**: Neon (Postgres) is the single source of truth.
- **Real-time Mirror**: Firestore mirrors SQL state for low-latency frontend consumption.
- **Temporal Isolation**: Strict `data_timestamp <= created_at` enforcement to prevent look-ahead bias.

## 5. Security
- **Credential Protection**: Hardened `.gitignore` and secret-scanning protocols.
- **Trading Safety**: `REAL_TRADING` and `BROKER_ORDER_ENABLED` are hard-coded to `FALSE` in the core configuration.
