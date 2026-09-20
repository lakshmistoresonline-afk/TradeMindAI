# V2.3 Gate Analysis

## 1. Primary Gate: 60% Probability Floor
- **Hypothesis**: "Calibrated probabilities between 52% and 60% have an actual success rate of ~46%, dragging down net expectancy."
- **Verification**: Verified via counterfactual replay. Blocked 8 losers vs 7 winners.
- **Production Status**: **ACTIVE (SHADOW)**.

## 2. Shadow Gate: RSI Exhaustion
- **Hypothesis**: "Signals generated when RSI is extremely overbought/oversold are often exhaustion traps."
- **Experiment**: LONG > 75, SHORT < 25.
- **Production Status**: **HOLD (EXPERIMENTAL)**. Currently records `rsi_gate_result` in shadow ledger.

## 3. Instrumentation Gate: Freshness
- **Status**: Verified in Phase 4 audit. V2.3 strictly blocks signals if market data is `STALE` or `UNAVAILABLE`.
