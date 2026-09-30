# TradeMind AI — Synthetic Data & Historical Ledger Audit

---

## 1. Audit Findings

1. **Historical Shadow Ledger**:
   - The 1,000 historical outcomes in `signals_history` were generated via deterministic backtesting outcome simulation (`node_update_all_data.js`) rather than real-time recorded historical execution.
2. **Classification**:
   - **HISTORICAL PERFORMANCE CLAIM NOT INDEPENDENTLY VERIFIED** from live broker execution logs (strictly a simulated historical shadow backtest).
3. **Live Market Quotes**:
   - Real-time spot quotes are fetched directly from Yahoo Finance API (`.NS`) and stored in `web/src/utils/livePrices.ts`.
