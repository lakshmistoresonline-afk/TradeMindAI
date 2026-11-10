# TradeMindAI — Phase D Signal Quality Gates Report

**Gate Services**: [backend/services/signal_validator_service.py](file:///D:/TradeMindAI/backend/services/signal_validator_service.py) & [backend/services/signal_quality_service.py](file:///D:/TradeMindAI/backend/services/signal_quality_service.py)

---

## 1. Multi-Tier Signal Quality & Publication Gates

A signal is published ONLY when it satisfies all required quality and publication criteria:
1. **Freshness Gate**: `FreshnessPolicy.get_status(data_timestamp)` must be `FRESH` (data age $< 15$ minutes) or `AGING` ($< 120$ minutes). Fails if `STALE` or `UNAVAILABLE`.
2. **Direction Gate**: `direction` must be explicitly `LONG`/`BUY` or `SHORT`/`SELL`. Rejects `NEUTRAL` or `UNAVAILABLE`.
3. **Price Finiteness & Geometry Gate**: Entry, Target, Stop prices must be finite, positive, geometrically valid, and yield $\text{RR} \ge 1.0$.
4. **Conviction Edge Gate**: `conviction >= 52%` (fails if conviction $< 52\%$).
5. **Traceability Gate**: Requires `provenance_id` trace link (fails if missing).
6. **Symbol Verification**: Requires valid canonical symbol string (length $\ge 2$).
7. **BUY-Only Eligibility**: `is_eligible_buy(signal)` requires `direction in ("BUY", "LONG")` and `rating == "BUY"`.
8. **Model Quality Gate**: Champion model must exist (`model is not None`), have test size $\ge 20$, and ROC AUC $> 0.52$ (SWING) / $> 0.65$ (LONG).
9. **Quarantine Enforcement**: All public/external API publication endpoints fail closed (HTTP 423 Quarantined).

---

## 2. Test Verification Summary

- `test_phase_d_weak_edge_conviction_rejected`: **PASSED**
- `test_phase_d_missing_provenance_rejected`: **PASSED**
- `test_phase_c_signal_quality_service_fails_closed_on_unregistered_or_weak_model`: **PASSED**
