# PHASE 2P: API & DASHBOARD PARITY

## 1. Serialization Audit
Verified that the `/shadow/active-signals` API correctly serializes the following F&O fields:
- `derivative_current` (NULL if missing)
- `price_status`
- `strike`
- `option_type`

## 2. Parity Check
`Neon.derivative_current == API.derivative_current == Dashboard.display_price`.

---
**Status**: PARITY_CERTIFIED.
