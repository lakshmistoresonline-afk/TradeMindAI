# TradeMind AI — Absolute Product Boundary & Signal-Only Architecture

---

## 1. Product Boundary Policy

**TradeMindAI is strictly a Signal-Provider and Market-Analysis Application.**

It is **NOT** a broker, trading terminal, execution engine, or automated trading system. It must **NEVER** execute real trades or manage live broker positions.

### Absolute Prohibitions (Non-Negotiable)

The application MUST NEVER:
1. Place a real market, limit, or stop order.
2. Submit, modify, or cancel a broker order.
3. Open, close, or manage a live broker position.
4. Automatically deploy capital or execute stop-losses/targets.
5. Store broker credentials capable of trading or request trading scopes.
6. Implement an order-execution worker or live trade executor.

---

## 2. System Architecture Flow

The system pipeline ends strictly at signal delivery to the user:

```text
MARKET DATA (NSE / Yahoo Finance)
      │
      ▼
FEATURE ENGINE (Technical, Volatility, Options)
      │
      ▼
REGIME ENGINE (HMM, Market Breadth)
      │
      ▼
ML & QUANT MODELS (Classification & Calibration)
      │
      ▼
SIGNAL QUALITY GATE (Filters & Checks)
      │
      ▼
PUBLISHED SIGNAL
      │
      ▼
USER INTERFACE (Read-Only Analysis)
```

There is **NO** production path from `SIGNAL` to `ORDER` or `BROKER`.

---

## 3. Configuration & Enforcement

1. **`REAL_TRADING = False` Enforcement**:
   - `backend/core/config.py` enforces `REAL_TRADING = False` with a Pydantic field validator that raises a `ValidationError` if any configuration attempt is made to set it to `True`.
2. **Automated Security Tests**:
   - `backend/tests/test_safety_boundary.py` contains automated `pytest` test cases verifying that `REAL_TRADING` fails closed.
3. **Analytical Terminology**:
   - "Stop-Loss" is labeled **"Invalidation Level"** (the price condition under which the analytical signal thesis is considered invalid).
   - "Position Sizing" is labeled **"Informational Position Sizer"**.
   - Execution buttons (`BUY NOW`, `EXECUTE`) are replaced with analytical actions (`AUDIT SIGNAL`, `VIEW EVIDENCE`).
