# Historical Signal Forensic Baseline

## 1. Audit Metadata
- **Repository HEAD**: `8a986345c7f1f7ef8579161db14117a46c6698d2`
- **Audit Date**: 2026-09-19
- **Environment**: Production Hardened

## 2. Architecture Discovery

### A. Signal Generation Engine
- **Master Node**: `SignalEngine.generate_signal` (backend/services/signal_engine.py)
- **Input**: Multi-agent consensus (Technical, SMC, Wyckoff, ML).
- **Core version**: Strategy V2.2.
- **Model**: "TradeMind Core v2.2".
- **Risk Geometry**: `RiskEngine` (ATR-based).
  - SHORT: 1.5 ATR Stop / 2.0 RR Target
  - SWING: 2.0 ATR Stop / 2.5 RR Target
  - LONG: 3.0 ATR Stop / 3.0 RR Target

### B. Signal Lifecycle & Outcome
- **Lifecycle FSM**: `SignalLifecycleService` manages states: CREATED -> WAITING_FOR_ENTRY -> ACTIVE -> TERMINAL.
- **Outcome Engine**: `OutcomeService.evaluate_signal_outcome`.
- **Truth Principles**:
  - Same-bar ambiguity: Detected and flagged as `AMBIGUOUS`.
  - Terminal Immutability: Enforced via `SignalLedgerService`.
  - Freshness Enforcement: Canonical policy (FRESH < 15m).

### C. Authoritative Ledger
- **Primary Source**: Neon PostgreSQL (`shadow_signals` table).
- **Mirror**: Firestore.
- **Forensic Evidence**: `ShadowProvenanceDB` stores input/output hashes and snapshot data.

### D. Market Data Architecture
- **Provider**: `PriceResolver` (Multi-provider failover: NSE Open -> AngelOne -> Upstox -> Dhan -> Groww -> YFinance).
- **Truth Model**: Distinguishes `observation_timestamp`, `received_at`, and `calculated_at`.
- **Bulk Fetching**: YahooQuery bulk requests for Index/VIX.

## 3. Signal Quality Gates (Current)
1. **Freshness**: Max 120h since last feature date (for generation).
2. **Liquidity**: Min 10M Avg Volume.
3. **Trend**: EMA 200 alignment.
4. **Momentum**: Breakout magnitude > 0.5 ATR.
5. **Edge**: Calibrated Probability >= 52%.
6. **Value**: Expected Value > 0.
7. **Volatility**: Risk % <= 12%.

---
**Status**: Architecture Audited & Documented.
**Next Action**: Connect to Neon and extract the V2.2 Shadow Population.
