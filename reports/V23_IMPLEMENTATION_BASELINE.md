# V2.3 Shadow Implementation Baseline

## 1. Audit Metadata
- **Repository HEAD**: `28e0d9b4387bda1febff86d447b9ec7d2431e9ac`
- **Audit Date**: 2026-09-20
- **Status**: **BASELINE ESTABLISHED**

## 2. Existing Architecture (V2.2 Production)

### A. Signal Flow
- **Generation**: `SignalEngine.generate_signal` (Multi-agent consensus).
- **Validation**: `SignalValidatorService` (Freshness, Geometry, Conviction > 52%).
- **Publication**: `SignalLedgerService.create_signal` (Atomic Neon write + thread-based Firestore mirror).
- **Monitoring**: `SignalLifecycleService` + `SignalAuditor`.

### B. Risk Geometry
- **Short**: 1.5 ATR Stop / 2.0 RR Target.
- **Swing**: 2.0 ATR Stop / 2.5 RR Target.
- **Long**: 3.0 ATR Stop / 3.0 RR Target.

### C. Calibration
- **Engine**: `CalibrationService`.
- **Method**: Platt Scaling (Sigmoid) with fixed coefficients per asset class.

### D. Instrumentation Status (Current)
- **Entry Timing**: `activated_at` and `trigger_price` exist in `LiveSignal` model but historical coverage is identified as 0% in forensics.
- **Regime**: `regime` exists but 65% of historical population is missing data.
- **Provenance**: `ShadowProvenanceDB` stores hashes of inputs and outputs.

## 3. Confirmed Objective
Implement a V2.3 Shadow Layer that:
1. **Never blocks V2.2 production signals**.
2. Applies a **60% Calibrated Probability Floor**.
3. Experiments with **RSI Exhaustion** (Shadow Only).
4. Full **Entry & Regime Instrumentation**.
5. Records all decisions in a `signal_shadow_decisions` ledger.

---
**Certified By**: Principal Quantitative Engineer (AI Agent)
