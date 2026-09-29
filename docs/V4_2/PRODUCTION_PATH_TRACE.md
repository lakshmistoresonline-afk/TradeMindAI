# TradeMind AI — Production Signal Path Trace (Step 12 & 13)

---

## 1. Single Authoritative Production Path

```text
1. DATA INGESTION
   ├── Yahoo Finance API (`.NS`) via `scripts/node_update_all_data.js`
   └── Saved locally to `web/src/utils/livePrices.ts`
             │
             ▼
2. SIGNAL GENERATION
   ├── `scripts/node_update_all_data.js`
   └── ATR(14) Volatility Scaling ($T_1, T_2, T_3$, Invalidation Level)
             │
             ▼
3. QUALITY GATE
   ├── `backend/services/signal_quality_gate.py`
   ├── `REAL_TRADING = False` Check
   ├── Options PCR >= 0.85 & Call Wall Clearance
   ├── VPIN Flow Toxicity <= 0.35
   └── 4/4 Swarm Consensus
             │
             ▼
4. CLOUD FIRESTORE MIRRORING
   ├── Active Signals -> `signals`
   └── Historical Signals -> `signals_history`
             │
             ▼
5. FRONTEND PRESENTATION
   ├── `web/src/hooks/useAITradeDecision.ts` (`mapCanonicalSignal`)
   └── `web/src/pages/EquitySignals.tsx` & `SignalDetail.tsx`
```

---

## 2. Duplicate Signal Engine Audit

- `backend/app/services/signal_engine.py`: Reconciled as offline local TA helper.
- `backend/services/signal_engine.py`: Isolated.
- **Authoritative Production Path**: All production signals are mirrored via `scripts/node_update_all_data.js` to Firestore and normalized via `web/src/hooks/useAITradeDecision.ts`.
