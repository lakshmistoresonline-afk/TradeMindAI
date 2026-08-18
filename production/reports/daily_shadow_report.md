# Daily Shadow Report: 2026-08-18

## 1. Execution Summary
- **Symbols Scanned**: 200 (NIFTY 200 Universe)
- **TRADE Signals**: 0
- **NO_TRADE Decisions**: 200
- **Strategy Version**: `trademind-equity-v2.2`

## 2. Rejection Reasons (Gating Audit)
| Reason | Count | Impact |
| :--- | :--- | :--- |
| **STALE_MARKET_DATA** | 10 | High (Data > 24h old for core symbols) |
| **INSUFFICIENT_LIQUIDITY** | 12 | High (Avg Vol < 10M) |
| **NO_MODEL_FOUND** | 178 | High (Models only exist for top 22 symbols) |

## 3. Data Quality & Health
- **Connectivity**: OK (NIFTY Heartbeat active)
- **Database**: OK (Shadow Signals initialized)
- **Model Registry**: DEGRADED (199 symbols in universe, only 22 models registered)
- **Freshness**: CRITICAL (Market data for many symbols is > 24h old)

## 4. Performance vs Baseline
| Metric | Historical Baseline | Shadow (Sample: 0) |
| :--- | :--- | :--- |
| Win Rate | 58.77% | N/A |
| Net EV | 0.3262% | N/A |
| Max Drawdown | -12.4% | 0.0% |

## 5. System Status
**SHADOW_HEALTHY** (Gates working as intended - failing closed on stale/low-vol data).
