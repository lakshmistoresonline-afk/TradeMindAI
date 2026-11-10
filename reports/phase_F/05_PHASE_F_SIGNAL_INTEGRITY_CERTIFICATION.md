# TradeMindAI — Phase F Signal Integrity Certification Report

**Audited Component**: [backend/services/signal_validator_service.py](file:///D:/TradeMindAI/backend/services/signal_validator_service.py) & [backend/services/signal_ledger_service.py](file:///D:/TradeMindAI/backend/services/signal_ledger_service.py)

---

## 1. Direction & Risk Geometry Audit Results

1. **Direction Integrity**:
   - `ALLOWED_DIRECTIONS = {"LONG", "BUY", "SHORT", "SELL"}`.
   - Rejects non-directional (`NEUTRAL`/`UNAVAILABLE`), missing, empty, or unknown directions (`NON_DIRECTIONAL_PREDICTION`).
2. **Price Finiteness & Positive Values**:
   - Entry, Target, Stop prices must satisfy `np.isfinite()` and be $> 0$.
3. **Risk Distance & Target Geometry**:
   - Zero risk distance ($|\text{Entry} - \text{Stop}| \le 1e-4$) rejected (`ZERO_RISK_DISTANCE`).
   - Long Target must be $> \text{Entry}$, Stop $< \text{Entry}$.
   - Short Target must be $< \text{Entry}$, Stop $> \text{Entry}$.
   - Geometric Risk/Reward ratio $\text{RR} = \frac{|\text{Target} - \text{Entry}|}{|\text{Entry} - \text{Stop}|}$ must be $\ge 1.0$.
4. **Terminal-State Immutability**:
   - Signals in terminal states (`TARGET_HIT`, `STOP_LOSS`, `EXPIRED`, `CANCELLED`, `AMBIGUOUS`) cannot be reopened or mutated.
5. **Transaction Ownership**:
   - Caller-owned sessions are flushed (`db.flush()`) without internal commit or close.

---

## 2. Test Execution Evidence

- `test_phase_d_valid_long_signal_passes_validation`: **PASSED**
- `test_phase_d_valid_short_signal_passes_validation`: **PASSED**
- `test_phase_d_neutral_or_unavailable_direction_rejected`: **PASSED**
- `test_phase_d_non_finite_price_rejected`: **PASSED**
- `test_phase_d_non_positive_price_rejected`: **PASSED**
- `test_phase_d_zero_risk_distance_rejected`: **PASSED**
- `test_phase_d_inverted_long_geometry_rejected`: **PASSED**
- `test_phase_d_inverted_short_geometry_rejected`: **PASSED**
- `test_phase_d_suboptimal_risk_reward_rejected`: **PASSED**
- `test_phase_d_weak_edge_conviction_rejected`: **PASSED**
- `test_phase_d_missing_provenance_rejected`: **PASSED**
