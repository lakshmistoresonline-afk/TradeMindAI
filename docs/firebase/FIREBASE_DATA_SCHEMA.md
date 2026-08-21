# Firebase Firestore Data Schema

This document outlines the schema used for the TradeMind AI application layer in Firestore.

## Collections

### 1. `stocks` (Stock Master)
- **Document ID**: `symbol` (e.g., `RELIANCE`)
- **Fields**:
    - `name`: string
    - `sector`: string
    - `industry`: string
    - `last_price`: number
    - `market_cap`: number
    - `is_fno`: boolean
    - `index_membership`: string (e.g., `NIFTY_200`)
    - `updated_at`: timestamp

### 2. `live_signals` (Active & Historical Signals)
- **Document ID**: `bt_{symbol}_{YYYYMMDD}` or UUID
- **Fields**:
    - `symbol`: string
    - `timestamp`: timestamp
    - `direction`: string (`LONG`, `SHORT`)
    - `conviction`: number (0-100)
    - `entry_price`: number
    - `target_price`: number
    - `stop_loss_price`: number
    - `status`: string (`ACTIVE`, `TARGET_HIT`, `STOP_LOSS`, `EXPIRED`)
    - `profit_pct`: number
    - `model_version`: string

### 3. `portfolio_trades` (Realized Executions)
- **Document ID**: `trade_{id}`
- **Fields**:
    - `trade_id`: string
    - `symbol`: string
    - `direction`: string
    - `entry_date`: timestamp
    - `exit_date`: timestamp
    - `entry_price`: number
    - `exit_price`: number
    - `quantity`: number
    - `net_pnl`: number
    - `transaction_costs`: number
    - `slippage`: number
    - `status`: string

### 4. `portfolio_equity` (Historical Performance)
- **Document ID**: `YYYY-MM-DD`
- **Fields**:
    - `date`: timestamp
    - `equity`: number
    - `cash`: number
    - `realized_pnl`: number
    - `unrealized_pnl`: number
    - `open_positions`: number

### 5. `performance_summary` (Aggregated Metrics)
- **Document ID**: `latest`
- **Fields**:
    - `total_net_pnl`: number
    - `total_return_pct`: number
    - `win_rate`: number
    - `profit_factor`: number
    - `max_drawdown`: number
    - `sharpe_ratio`: number
    - `last_updated`: timestamp
