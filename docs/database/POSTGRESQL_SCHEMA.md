# PostgreSQL Operational Schema

## 1. Core Market Data
### `stocks`
- `symbol` (PK, varchar)
- `name` (varchar)
- `sector` (varchar)
- `industry` (varchar)
- `last_price` (decimal)
- `change_pct` (decimal)
- `market_cap` (bigint)
- `pe_ratio` (decimal)
- `pb_ratio` (decimal)
- `updated_at` (timestamp)

### `historical_prices`
- `id` (PK, uuid)
- `symbol` (FK)
- `date` (date)
- `open` (decimal)
- `high` (decimal)
- `low` (decimal)
- `close` (decimal)
- `volume` (bigint)
- `indicators` (jsonb) # Stores EMA, RSI etc for fast dashboard retrieval

## 2. Institutional Intelligence
### `market_regimes`
- `id` (PK)
- `date` (date)
- `regime` (varchar) # BULL, BEAR
- `risk_mode` (varchar)
- `description` (text)
- `volatility_index` (decimal)

### `intel_reports`
- `id` (PK)
- `type` (varchar) # CLOSING, MORNING
- `date` (date)
- `summary` (text)
- `key_events` (jsonb)
- `ai_bias` (varchar)

### `predictions`
- `id` (PK)
- `symbol` (varchar)
- `date` (timestamp)
- `model_version` (varchar)
- `prediction` (varchar) # UP, DOWN
- `confidence` (decimal)
- `metadata` (jsonb)

## 3. System & Forensics
### `model_registry`
- `id` (PK)
- `name` (varchar)
- `symbol` (varchar)
- `version` (varchar)
- `accuracy` (decimal)
- `is_champion` (boolean)
- `last_trained` (timestamp)

### `backtests`
- `symbol` (PK)
- `total_signals` (int)
- `success_rate` (decimal)
- `avg_profit` (decimal)
- `last_run` (timestamp)
