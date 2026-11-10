# TradeMindAI — Phase D Risk Geometry Report

**Gate Service**: [backend/services/signal_validator_service.py](file:///D:/TradeMindAI/backend/services/signal_validator_service.py)  
**Risk Service**: [backend/services/risk_engine.py](file:///D:/TradeMindAI/backend/services/risk_engine.py)

---

## 1. Geometric Risk & Target Level Contracts

### LONG / BUY Geometry
- **Stop Loss**: $\text{Stop} < \text{Entry}$
- **Target**: $\text{Target} > \text{Entry}$
- **Risk Distance**: $\text{Risk} = \text{Entry} - \text{Stop}$
- **Reward Distance**: $\text{Reward} = \text{Target} - \text{Entry}$

### SHORT / SELL Geometry
- **Stop Loss**: $\text{Stop} > \text{Entry}$
- **Target**: $\text{Target} < \text{Entry}$
- **Risk Distance**: $\text{Risk} = \text{Stop} - \text{Entry}$
- **Reward Distance**: $\text{Reward} = \text{Entry} - \text{Target}$

---

## 2. Risk/Reward Ratio Calculation & Hard Thresholds

$$\text{RR}_{\text{calculated}} = \frac{|\text{Target} - \text{Entry}|}{|\text{Entry} - \text{Stop}|}$$

- **Zero Risk Distance Guard**: If $|\text{Entry} - \text{Stop}| \le 1e-4 \implies$ Rejected (`ZERO_RISK_DISTANCE`).
- **Minimum Risk/Reward Guard**: If $\text{RR}_{\text{calculated}} < 1.0 \implies$ Rejected (`SUBOPTIMAL_RISK_REWARD`).
- **Inverted Levels Guard**: If Long Target $\le$ Entry or Long Stop $\ge$ Entry, or Short Target $\ge$ Entry or Short Stop $\le$ Entry $\implies$ Rejected (`INVALID_LEVELS`).
- **Finiteness Guard**: If Entry, Target, or Stop contains `NaN` or `np.inf` $\implies$ Rejected (`NON_FINITE_PRICES`).

---

## 3. Test Verification Summary

- `test_phase_d_non_finite_price_rejected`: **PASSED**
- `test_phase_d_non_positive_price_rejected`: **PASSED**
- `test_phase_d_zero_risk_distance_rejected`: **PASSED**
- `test_phase_d_inverted_long_geometry_rejected`: **PASSED**
- `test_phase_d_inverted_short_geometry_rejected`: **PASSED**
- `test_phase_d_suboptimal_risk_reward_rejected`: **PASSED**
