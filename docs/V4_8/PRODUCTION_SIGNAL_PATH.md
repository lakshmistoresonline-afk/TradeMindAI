# TradeMind AI — V4.8 Production Signal Path Trace

---

## 1. Single Authoritative Production Path

```text
Yahoo Finance API (`livePrices.ts`)
       │
       ▼
Signal Generator (`scripts/node_update_all_data.js`)
       │ (ATR Volatility Scaling, VPIN, PCR, Swarm)
       ▼
Signal Quality Gate (`backend/services/signal_quality_gate.py`)
       │ (`REAL_TRADING = False` Check)
       ▼
Firestore Cloud Database (`signals` & `signals_history`)
       │
       ▼
Frontend Normalizer (`web/src/hooks/useAITradeDecision.ts`)
       │
       ▼
Next.js UI Terminology (`SignalCard.tsx` — Invalidation Level)
```
