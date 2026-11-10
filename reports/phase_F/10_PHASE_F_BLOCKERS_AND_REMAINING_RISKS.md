# TradeMindAI — Phase F Blockers & Remaining Risks Report

**Final Certification Decision**: **`READY FOR QUARANTINED STAGING`**

---

## 1. Protected File Fallback Blockers (`backend/services/signal_engine.py`)

1. **In-line Fallback Defect (Lines 50-95)**:
   - Contains dynamic feature calculation fallback when `features_list` is empty that uses simple rolling mean RSI instead of Wilder smoothing, un-guarded EMA200 calculation, and constant fallbacks (`0.02 * price` for ATR, `50.0` for RSI).
   - **Protection Status**: `signal_engine.py` is protected by safety instructions and cannot be edited without explicit user authorization.
2. **Direction Mapping Defect (Line 125)**:
   - Line 125 maps `direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"`, converting `NEUTRAL` or `UNAVAILABLE` into `SHORT`.
   - **Protection Status**: `signal_engine.py` is protected by safety instructions and cannot be edited without explicit user authorization.
   - **Upstream Fail-Closed Mitigation**: In `EquitySignalGenerationService`, `SignalValidatorService`, and `SignalLedgerService`, TradeMindAI enforces BUY-only publication eligibility (`is_eligible_buy(signal)`), so all non-BUY / `SHORT` signals are immediately rejected and blocked from publication.

---

## 2. Unresolved Configuration File Hash (`backend/core/config.py`)

1. **`backend/core/config.py`**:
   - Working-tree hash (`DE72514D02E1...`) differs from Git HEAD (`3C671487E46F...`).
   - Preserved untouched per safety instructions.

---

## 3. Mandatory Safety Invariants Re-Certification

```python
REAL_TRADING = False
LIVE_EXECUTION_ENABLED = False
BROKER_ORDER_EXECUTION_ENABLED = False
QUARANTINE_ACTIVE = True
SIGNALS_ONLY_ARCHITECTURE = True
```

- **Compliance Status**: **100% ENFORCED**. Zero live trading or broker execution paths introduced or enabled.
