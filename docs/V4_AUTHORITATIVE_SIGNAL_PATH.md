# TradeMind AI — V4 Authoritative Signal Path Audit

---

## 1. Single Authoritative Production Path

To eliminate competing or ambiguous signal generation paths across `backend/app/services/signal_engine.py` and `backend/services/signal_engine.py`, TradeMindAI enforces **one single, unified production signal pipeline**.

```text
1. MARKET DATA INGESTION
   ├── Live NSE Spot Prices via Yahoo Finance API (`.NS`)
   └── Saved locally to `web/src/utils/livePrices.ts`
             │
             ▼
2. SIGNAL GENERATION & RISK GEOMETRY
   ├── `scripts/node_update_all_data.js`
   ├── Strategy V5.0 God Mode Pipeline
   └── ATR(14) Volatility Scaling ($T_1, T_2, T_3$, Invalidation Level)
             │
             ▼
3. QUALITY GATE AUDIT
   ├── `backend/services/signal_quality_gate.py`
   ├── `REAL_TRADING = False` Safety Check
   ├── Options PCR >= 0.85 & Call Wall Clearance
   ├── VPIN Toxicity <= 0.35
   └── 4/4 AI Swarm Consensus
             │
             ▼
4. CLOUD FIRESTORE MIRRORING
   ├── Active Signals -> `signals` collection
   └── Historical Signals -> `signals_history` collection
             │
             ▼
5. USER TERMINAL INTERFACE
   ├── `web/src/hooks/useAITradeDecision.ts` (`mapCanonicalSignal`)
   ├── Active Signals Terminal (`/signals` - Active)
   ├── History Terminal (`/signals` - History)
   └── Forensic Evidence View (`/signals/{id}`)
```

---

## 2. Unambiguous Production Service Mapping

* **Production Generator Script**: `scripts/node_update_all_data.js`
* **Production Quality Gate**: `backend/services/signal_quality_gate.py`
* **Production Model Object**: `backend/domain/models/ios.py` (`LiveSignal`)
* **Production Frontend Normalizer**: `web/src/hooks/useAITradeDecision.ts` (`mapCanonicalSignal`)
