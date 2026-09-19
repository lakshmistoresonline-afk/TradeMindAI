# Historical Signal Forensic Baseline

## 1. Audit Metadata
- **Verified HEAD SHA**: `8a986345c7f1f7ef8579161db14117a46c6698d2`
- **Audit Date**: 2026-09-19
- **Authoritative Database**: Neon (PostgreSQL)

## 2. System Architecture (Current HEAD)

### A. Signal Generation
- **Engine**: `SignalEngine.generate_signal` (V2.2 Strategy).
- **Core Version**: `v2.2`.
- **Decision Logic**: Multi-agent consensus (Technical, SMC, Wyckoff, ML).
- **Risk Multipliers**: 
  - **SHORT**: 1.5 ATR Stop / 2.0 RR Target.
  - **SWING**: 2.0 ATR Stop / 2.5 RR Target.
  - **LONG**: 3.0 ATR Stop / 3.0 RR Target.

### B. Outcome Resolution
- **Service**: `OutcomeService.evaluate_signal_outcome`.
- **States**: `TARGET_HIT`, `STOP_LOSS`, `EXPIRED`, `CANCELLED`, `TIMEOUT`, `AMBIGUOUS`.
- **Same-Bar Ambiguity**: Explicitly detected when High >= Target AND Low <= Stop in the same candle. Results in `AMBIGUOUS`.

### C. Authoritative Ledger
- **Shadow Signals**: `shadow_signals` table (Reconstructed and historical population).
- **Live Signals**: `live_signals` table (Active production signals).
- **Provenance**: `ShadowProvenanceDB` stores bitwise evidence hashes.

### D. Market Data & Freshness
- **Service**: `MarketDataService` & `PriceResolver`.
- **Policy**: `FRESH` (< 15m), `AGING` (15-120m), `STALE` (> 120m).
- **Instrumentation**: Separates `observation_timestamp`, `received_at`, and `calculated_at`.

## 3. Discovered Population Segmentation (V2.2)
- **Total Ledger Population**: 166 signals.
- **Group 1 (S:3.0% / T:3.0%)**: Legacy Fixed Geometry (RR:1.0). N=24 resolved.
- **Group 2 (S:4.0% / T:10.0%)**: SWING Standard Geometry (RR:2.5). N=26 resolved.
- **Group 3 (Active)**: Live production signals in `ACTIVE` state. N=113 (Shadow) + 33 (Live).

---
**Certified By**: Principal Quantitative Engineer (AI Agent)
