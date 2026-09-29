# TradeMind AI — Data Provenance Audit Report (Step 28)

---

## 1. Data Provenance Matrix

| Data Component | Primary Source | Timestamp | Transformation Function | Production Consumer | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Spot Price Quotes** | Yahoo Finance API (`.NS`) | $t$ (15m interval) | `fetchLiveMarketPrices()` | `livePrices.ts` | `VERIFIED` |
| **Active Signals** | Firestore (`signals`) | $t$ (Real-Time) | `node_update_all_data.js` | `EquitySignals.tsx` | `VERIFIED` |
| **Historical Signals**| Firestore (`signals_history`)| $t$ (10-Year Ledger)| `node_update_all_data.js` | `EquitySignals.tsx` | `VERIFIED` |
| **Signal Normalizer** | Frontend Hook | $t$ (On Mount) | `mapCanonicalSignal()` | `useAITradeDecision.ts` | `VERIFIED` |
