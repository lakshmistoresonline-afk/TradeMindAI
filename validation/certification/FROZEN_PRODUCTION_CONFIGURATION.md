# Frozen Production Configuration: Equity Swing Trading v2.2

## 1. Core Logic
*   **Asset Class**: Equity
*   **Strategy Type**: Swing (Mean Reversion / Trend Following Hybrid)
*   **Universe**: NIFTY 200 (199 symbols with history)
*   **Horizon**: 20 bars (approx. 4 weeks for daily timeframe)

## 2. Gating Filters (No-Trade Engine)
*   **Confidence Gate**: Calibrated Probability must be ≥ 0.52.
*   **Trend Gate**: Rejects signals contrary to the 200-period EMA.
*   **Magnitude Gate**: Rejects signals where the current price is within 0.5 ATR of the 20-period SMA (prevents trading in non-volatile noise).

## 3. Risk & Reward
*   **Fixed Target**: 3.0%
*   **Fixed Stop**: 3.0% (1:1 Reward/Risk ratio)
*   **Conservative Resolution**: STOP LOSS is assumed to be hit first if both Target and Stop are reached in the same candle.

## 4. Model Architecture
*   **Engine**: Random Forest Classifier.
*   **Regularization**: Max Depth 5, Min Samples Leaf 10 to ensure generalization.
*   **Labels**: Binary "UP" (Positive 5-day return) vs "DOWN".

## 5. Economic Assumptions
*   **Transaction Costs**: 0.05% per leg.
*   **Slippage**: 0.05% per leg.
*   **Total Friction**: 0.20% per round trip (subtracted from gross returns).
