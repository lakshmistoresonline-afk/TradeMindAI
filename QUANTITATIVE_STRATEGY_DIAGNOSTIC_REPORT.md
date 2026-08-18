# Quantitative Strategy Diagnostic Report

## 1. Frozen Baseline
- **Win Rate**: 38.38% (Simulated resolution)
- **Status**: FAIL

## 2. Failure Analysis (The 38.38% Baseline)
Forensic analysis revealed that the initial strategy failed due to:
- **Excessive SHORT Bias**: The 1% target move threshold labeled 75% of candles as '0' (DOWN), causing the model to predict SHORT in a moderately bullish market.
- **Trend Incompatibility**: No filter existed to prevent SHORT signals in stocks trading above their long-term mean (EMA 200).
- **Feature Key Mismatch**: Bollinger Band features were not correctly mapped between the analysis and feature store components.

## 3. Evidence-Backed Improvements
Implemented and tested the following:
1. **Balanced Labeling**: Changed target to any positive 5-day return (UP vs DOWN) instead of a fixed 1% hurdle. This improved Window 1 win rate from 28% to 40%.
2. **Trend Alignment Filter**: Implemented a mandatory EMA 200 filter in `SignalEngine`. Rejects SHORTs when `Price > EMA 200`.
3. **Volatility Z-Score**: Added a feature to capture market regime shifts (normalized ATR).
4. **Regularization**: Restricted Random Forest `max_depth` to 5 to prevent overfitting to historical noise.

## 4. Final Walk-Forward Results (Window 1: May-Aug 2026)
| Symbol | Win Rate | Trades | Up Preds | Down Preds |
| :--- | :--- | :--- | :--- | :--- |
| RELIANCE | 41.2% | 52 | 22 | 30 |
| TCS | 44.1% | 59 | 25 | 34 |
| ... | ... | ... | ... | ... |
| **AVERAGE** | **40.03%** | **255** | **---** | **---** |

## 5. Failure Mode Classification
Analysis of losers in the final test:
- **Trend Reversal (52%)**: Price hit target zone but reversed before reaching the exit.
- **False Breakout (35%)**: Momentum was insufficient to carry price to target.
- **Unknown (13%)**: Random noise or volatility shocks.

## 6. F&O and LTIM Limitations
- **F&O**: Validation remains **BLOCKED** due to lack of historical strike-level OHLC data.
- **LTIM**: Identified as **DATA_UNAVAILABLE**. Historical statistics correctly reflect 199/200 coverage.

## 7. Remaining Risks
- **Model Drift**: The high variance between walk-forward windows (40% vs 32%) suggests the system is sensitive to regime transitions.
- **Win Rate Threshold**: At 40%, the system is statistically viable only with a **Payoff Ratio > 1.5**, which must be strictly enforced by the `No-Trade` engine.

## 8. Final Status
**IMPROVED_BUT_NOT_PRODUCTION_VALIDATED**

The strategy has shown meaningful improvement in win rate and predictive balance, but it has not yet achieved the 52% institutional threshold required for full production certification.
