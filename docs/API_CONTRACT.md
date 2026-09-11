# TradeMind AI: Canonical Equity API Contract

## Base URL
`https://trademind-api-production.up.railway.app/api/v1`

## Endpoints

### 1. GET /equity/signals
Returns all equity signals from the authoritative Neon ledger.
- **Parameters**: `status`, `symbol`, `limit`, `page`
- **Response**: `List[EquitySignalDTO]`

### 2. GET /equity/signals/{signal_id}
Returns complete detail for a specific signal including lineage and outcome.
- **Response**: `EquitySignalDetailDTO`

### 3. GET /equity/scanner
Consolidated view for the Equity Scanner UI (Signals + Stock metadata).
- **Response**: `List[ScannerSignalDTO]`

### 4. GET /equity/performance
Canonical performance metrics for the frozen V2.2 strategy.
- **Response**: `ResearchMetricsDTO`

### 5. GET /equity/market
Current market regime and universe status.
- **Response**: `MarketStateDTO`

### 6. GET /system/health
Real-time health status of all subsystems (API, DB, Market Data, V2.2 Engine).
- **Response**: `SystemHealthDTO`

## Data Models (DTOs)

### EquitySignalDTO
```json
{
  "id": "sig_SYMBOL_TIMESTAMP",
  "symbol": "TCS",
  "direction": "LONG",
  "entry_price": 4200.50,
  "target_price": 4410.50,
  "stop_price": 4095.50,
  "calibrated_probability": 0.62,
  "expected_value": 45.20,
  "status": "ACTIVE",
  "created_at": "2026-09-11T10:00:00Z"
}
```
