# TradeMind AI — Frontend Analytical Terminology Audit (Step 11 & 36)

---

## 1. Terminology Audit Results

The entire frontend source code in `web/src/` was searched for execution-oriented wording.

| UI Location | Old Terminology | Reconciled Analytical Terminology | Purpose |
| :--- | :--- | :--- | :--- |
| `SignalCard.tsx` | `STOP LOSS` | **`INVALIDATION LEVEL`** | Analytical price threshold where thesis becomes invalid |
| `SignalCard.tsx` | `STOP LOSS (BREAKEVEN LOCKED)` | **`INVALIDATION (BREAKEVEN LOCKED)`** | Ratcheted breakeven analytical threshold |
| `SignalCard.tsx` | `BUY NOW` | **`ENTRY TRIGGERED — BREAKOUT CONFIRMED`** | Confirmed analytical price breakout trigger |
| `SignalCard.tsx` | `POSITION SIZER` | **`INFORMATIONAL POSITION SIZER`** | Clarifies that no automated order placement occurs |
| `SignalDetail.tsx` | `STOP LOSS` | **`INVALIDATION LEVEL`** | Analytical thesis invalidation boundary |
| `EquitySignals.tsx` | `TERMINAL` / `AUDIT` | **`AUDIT SIGNAL →`** | Analytical evidence navigation action |
