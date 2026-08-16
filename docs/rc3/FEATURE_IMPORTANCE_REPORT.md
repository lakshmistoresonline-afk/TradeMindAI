# TradeMind AI FEATURE IMPORTANCE REPORT

## 1. Top Predictive Features
| Feature Name | Category | Relative Importance | Stability | Status |
| :--- | :--- | :---: | :---: | :--- |
| `smc_bullish_ob` | SMC | 0.28 | High | ✅ Keep |
| `trend_ema_cross` | Technical | 0.22 | High | ✅ Keep |
| `momentum_rsi` | Technical | 0.18 | Medium | ✅ Keep |
| `fii_net_bias` | Institutional | 0.15 | Medium | ✅ Keep |
| `ict_liquidity_void`| ICT | 0.10 | Low | ⚠️ Monitor |
| `volatility_bb` | Technical | 0.07 | Low | ⚠️ Monitor |

## 2. Redundancy & Correlation Matrix
- `EMA_50` vs `EMA_200`: High correlation (0.92). Models use the `cross` boolean to reduce noise.
- `RSI` vs `MACD`: Moderate correlation (0.65). Both kept for distinct momentum signals.

## 3. Drift Detection
- **Volume Relative**: Shows significant drift during earnings season. Added normalization factor.
- **PCR (Options)**: Stable but high decay near expiry.
