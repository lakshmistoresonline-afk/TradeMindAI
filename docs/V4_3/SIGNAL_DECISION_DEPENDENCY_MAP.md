# TradeMind AI — Signal Decision Dependency Map (Step 38)

---

## 1. Signal Quality Gate Dependency Map

The Signal Quality Gate (`backend/services/signal_quality_gate.py`) evaluates every candidate signal against 6 dependent feature gates:

```text
CANDIDATE SIGNAL
       │
       ├── 1. SAFETY GATE: REAL_TRADING == False (Fail-closed)
       │
       ├── 2. VOLATILITY GATE: ATR(14) Scaled Entry, Targets & Invalidation
       │
       ├── 3. DERIVATIVES GATE: Options PCR >= 0.85 & Call Wall Clearance >= +0.50%
       │
       ├── 4. MICROSTRUCTURE GATE: VPIN Toxicity <= 0.35 & Order Book OIB >= +0.35
       │
       ├── 5. TREND SYNC GATE: Daily 200-SMA, Hourly 20-EMA/50-EMA, 5m RSI
       │
       └── 6. SWARM GATE: 4-Agent Unanimity (4/4 Approved = 100% Consensus)
               │
               ▼
        PUBLISH SIGNAL
```
