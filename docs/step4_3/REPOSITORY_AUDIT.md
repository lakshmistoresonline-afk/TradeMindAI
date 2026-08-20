# TradeMind AI - Step 4.3 Repository Audit

This audit identifies the files and components used in the Step 4.3 Robustness Validation.

## 1. Input Data (Read-Only)
| File | Purpose | Step 4.3 Usage | Safety |
| :--- | :--- | :--- | :--- |
| `docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json` | Canonical Trade-Level Results | Primary input for all robustness tests. | READ-ONLY (SHA-256 Verified) |
| `data/results/portfolio_trades.csv` | Executed Portfolio Trades | Verified ledger for trade-order randomization. | READ-ONLY |
| `data/results/portfolio_daily_equity.csv` | Portfolio Equity Curve | Baseline for OOS comparison. | READ-ONLY |
| `backend/local_operational.db` | Historical OHLC Prices | Source for liquidity and MTM audits. | READ-ONLY |

## 2. Core Logic (Read-Only)
| File | Component | Status |
| :--- | :--- | :--- |
| `backend/services/outcome_engine.py` | Trade Lifecycle Logic | FROZEN (No changes allowed) |
| `scripts/accuracy/portfolio_simulator.py` | Portfolio Accounting | FROZEN (No changes allowed) |

## 3. Validation Logic (Modifiable)
| File | Component | Purpose |
| :--- | :--- | :--- |
| `scripts/accuracy/walk_forward_v2.py` | Walk-Forward Engine | If supported, will be used for time-series validation. |
| `scripts/accuracy/feature_audit.py` | Look-Ahead Auditor | Used for Phase 4 Audit. |

## 4. Risks Identified
- **Survivorship Bias**: Universe contains exactly 200 current constituents. HistoricalConstituents are missing.
- **Look-Ahead**: Indicators computed in `run_step4_backtest.py` use windowing; verification required to ensure no future leakage.
