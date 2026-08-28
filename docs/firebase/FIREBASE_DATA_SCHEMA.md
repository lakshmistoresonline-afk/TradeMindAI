# Firebase Firestore Data Schema v2.0

## Collections

### 1. `stocks`
- **Purpose**: NIFTY 200 symbol master and metadata.
- **Document ID**: `symbol` (e.g., `RELIANCE`)
- **Fields**:
    - `name`: string
    - `sector`: string
    - `industry`: string
    - `last_price`: number
    - `market_cap`: number
    - `is_fno`: boolean
    - `index_membership`: string
    - `status`: string (`OPERATIONAL`, `DATA_UNAVAILABLE`)
    - `updated_at`: timestamp

#### Sub-collection: `prices`
- **Document ID**: `YYYY-MM-DD`
- **Fields**: `open`, `high`, `low`, `close`, `volume`, `timestamp`

### 2. `live_signals`
- **Purpose**: Historical validation and backtest signals.
- **Document ID**: `val_{symbol}_{timestamp}`
- **Fields**:
    - `symbol`: string
    - `direction`: string
    - `score`: number
    - `entry`: number
    - `target`: number
    - `stop`: number
    - `status`: string (`TARGET_HIT`, `STOP_LOSS`, `EXPIRED`)
    - `timestamp`: timestamp

### 3. `shadow_signals`
- **Purpose**: Real-time unseen market observation signals.
- **Document ID**: `sig_{symbol}_{timestamp}`
- **Fields**: same as `live_signals` + `shadow_only: true`.

### 4. `portfolio_equity`
- **Purpose**: Equity curve for historical and shadow accounts.
- **Document ID**: `type_{YYYY-MM-DD}` (e.g., `backtest_2026-08-21`)
- **Fields**: `date`, `equity`, `cash`, `realized_pnl`, `open_positions`

### 5. `performance_summary`
- **Purpose**: High-level KPI for each validation phase.
- **Document ID**: `backtest`, `walk_forward`, `shadow`
- **Fields**: `total_return`, `win_rate`, `profit_factor`, `max_drawdown`, `expectancy`

### 6. `market_regimes`
- **Purpose**: Economic environment tracking.
- **Document ID**: `YYYY-MM-DD`
- **Fields**: `regime` (BULL/BEAR), `vix`, `sentiment`, `description`

### 7. `shadow_scan_diagnostics`
- **Purpose**: Per-symbol gate audit for shadow trading.
- **Document ID**: `diag_{symbol}_{timestamp}`
- **Fields**: `symbol`, `score`, `decision`, `reason`, `age_hours`, `timestamp`

### 8. `system_status`
- **Purpose**: Infrastructure health and last sync metadata.
- **Document ID**: `latest`
- **Fields**: `market_status`, `last_data_update`, `last_shadow_run`, `operational_count`
