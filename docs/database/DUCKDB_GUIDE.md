# DuckDB Analytical Engine Guide

## 🔬 Purpose
DuckDB is integrated as the **high-speed analytical tier** for TradeMind AI. It is used to query large time-series datasets stored as **Parquet** files on disk.

## 📁 Storage Structure
- **Path**: `backend/data/features/`
- **Format**: `[SYMBOL].parquet`
- **Columns**: `date` (index), plus 30+ standardized AI features.

## 🚀 Key Workflows

### 1. Feature Engineering Ingestion
Feature vectors are appended to the symbol's Parquet file.
```python
# Via Repository
await data_platform_repo.save_feature_vector(vector)
```

### 2. ML Training Dataset Creation
ML models can fetch 5-10 years of data in milliseconds for retraining.
```python
# Via Analytical Engine
df = analytical_engine.create_ml_dataset("RELIANCE", "2019-01-01", "2024-01-01")
```

### 3. Historical Anomaly Search
Ad-hoc SQL queries can be run across the entire feature store.
```python
results = analytical_engine.query_features("SELECT * FROM 'backend/data/features/*.parquet' WHERE momentum_rsi > 0.9")
```

## 🛠️ Maintenance
- **Cleanup**: Unused symbols' Parquet files should be archived.
- **Deduplication**: Ingestion logic automatically ensures unique dates per file.
