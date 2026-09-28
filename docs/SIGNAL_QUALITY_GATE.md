# TradeMind AI — Signal Quality Gate Specification

---

## 1. Quality Gate Architecture

Before any generated signal is published to the live ledger, it must pass through the **Signal Quality Gate** (`backend/services/signal_quality_gate.py`).

---

## 2. Gate Verification Rules

1. **`REAL_TRADING = False` Safety Check**: Fails closed if any execution engine attempt is detected.
2. **ATR Volatility Geometry**: Ensures Entry, Targets ($T_1, T_2, T_3$), and Invalidation Level are scaled to $\text{ATR}_{14}$.
3. **Options Call Wall Clearance**: Entry price must be clear of the highest Call Open Interest strike wall by at least $+0.50\%$.
4. **VPIN Flow Toxicity**: Requires $VPIN \le 0.35$ (clean institutional accumulation).
5. **Multi-Timeframe Trend Sync**: Requires Daily 200-SMA, Hourly 20-EMA/50-EMA, and 5m RSI momentum alignment.
6. **4-Agent AI Swarm Unanimity**: Requires $100\%$ consensus across Technical, Derivatives, Microstructure, and Macro AI agents.

---

## 3. Decision Outputs

- **`PUBLISH`**: Signal passes all quality criteria $\rightarrow$ Mirrored to `signals` collection.
- **`BLOCK` / `NO_SIGNAL`**: Signal fails one or more criteria $\rightarrow$ Rejected from publication.
