# Phase 4 Quantitative Baseline

## 1. Frozen Metrics
*   **Win Rate**: 40.03%
*   **Brier Score**: 0.285
*   **Payoff Ratio**: 1.85
*   **Net EV per Trade**: ~0.42% (Current implementation)
*   **Max Drawdown**: -12.4%

## 2. Configuration Snapshot
*   **Target Definition**: Any positive 5-day future return.
*   **EMA-200 Filter**: Active (Rejects SHORT if Price > EMA200, LONG if Price < EMA200).
*   **Model**: Random Forest (Depth 5) to mitigate overfitting.
*   **Friction**: 0.05% cost + 0.05% slippage per leg.

## 3. Known Issues Identified
*   **EV Math Discrepancy**: Friction is currently calculated as a percentage of the (Target + Stop) distance, rather than the total transaction value. This likely overestimates Net EV.
*   **Regime Sensitivity**: Performance varies significantly across time windows (40% vs 32%).
*   **Label Noise**: "Any positive return" may be too sensitive to minor noise.
