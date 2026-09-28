# TradeMind AI — Authoritative Production Signal Path

---

## 1. Single Authoritative Pipeline Overview

To eliminate competing or ambiguous signal generation paths, TradeMindAI enforces **one single, unified production signal pipeline**.

```text
1. MARKET DATA INGESTION (NSE Spot / Yahoo Finance API)
             │
             ▼
2. DATA VALIDATION & FRESHNESS CHECK
             │
             ▼
3. FEATURE ENGINEERING & MULTI-TIMEFRAME ANALYSIS
             │
             ▼
4. REGIME DETECTION (Gaussian HMM & Market Breadth)
             │
             ▼
5. ML PREDICTION & CONFORMAL CALIBRATION
             │
             ▼
6. CROSS-SECTIONAL RANKING (NIFTY-200 Percentiles)
             │
             ▼
7. SIGNAL QUALITY GATE (ATR, Options PCR, VPIN, Swarm)
             │
             ▼
8. FIRESTORE SIGNAL PUBLICATION (`signals` & `signals_history`)
             │
             ▼
9. USER TERMINAL INTERFACE (Read-Only Presentation)
```

---

## 2. Reconciled Components & Services

* **Data Model**: `backend/domain/models/ios.py` (`LiveSignal`)
* **Quality Gate**: `backend/services/signal_quality_gate.py` (`SignalQualityGate`)
* **Database Mirror**: Firestore collections `signals` (Active) and `signals_history` (Historical)
* **Frontend Normalizer**: `web/src/hooks/useAITradeDecision.ts` (`mapCanonicalSignal`)

---

## 3. Signal Lifecycle & Outcome Tracking

Every published signal moves through a deterministic lifecycle:
1. **`WAITING_FOR_ENTRY`**: Signal generated; price is below breakout entry trigger.
2. **`ENTRY_TRIGGERED` / `ACTIVE`**: Price touches or crosses breakout entry price.
3. **`TARGET_HIT`**: Price hits Target 1 ($T_1$), Target 2 ($T_2$), or Target 3 ($T_3$).
4. **`STOP_LOSS` / `INVALIDATED`**: Price touches invalidation level ($SL$).
5. **`EXPIRED`**: Signal time horizon elapsed without entry trigger.
