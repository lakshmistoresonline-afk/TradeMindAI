# Step 4.4.1 Repository Audit

## 1. Input Source
- **Step 4.2 Baseline**: `docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json`
- **Portfolio Trades**: `data/results/portfolio_trades.csv`
- **Daily Equity History**: `data/results/portfolio_daily_equity.csv`

## 2. Walk-Forward Components
- **Orchestrator**: `scripts/accuracy/step4_4_walk_forward.py`
- **Portfolio Wrapper**: `scripts/accuracy/walk_forward_portfolio.py`
- **ML Retraining Logic**: Embedded in `step4_4_walk_forward.py` (RandomForest + Platt Scaling).
- **Execution Engine**: `backend/services/outcome_engine.py` (FROZEN).
- **Portfolio Engine**: `scripts/accuracy/portfolio_simulator.py` (FROZEN).

## 3. Discrepancy Scripts
- **Report A Generator**: `scripts/accuracy/step4_4_report_gen.py`
- **Report B Generator**: `scripts/accuracy/walk_forward_portfolio.py`

## 4. Database
- **Historical Prices**: `backend/local_operational.db` (Table: `historical_prices`).
- **Stock Master**: `backend/local_operational.db` (Table: `stocks`).

## 5. Audit Status
| Component | Status | Safety |
| :--- | :--- | :--- |
| OutcomeEngine | FROZEN | DO NOT MODIFY |
| PortfolioSimulator | FROZEN | DO NOT MODIFY |
| Step 4.2 Baseline | FROZEN | READ-ONLY |
| Step 4.4 Results | DISCREPANCY | TO BE RECONCILED |
