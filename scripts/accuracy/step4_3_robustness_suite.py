import json
import pandas as pd
import numpy as np
import os
import sys
import yaml
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from scripts.accuracy.portfolio_simulator import PortfolioBacktestEngine

def run_robustness():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    config_path = 'config/portfolio_backtest.yaml'
    db_path = 'backend/local_operational.db'

    engine = PortfolioBacktestEngine(config_path, results_path, db_path)

    # 1. Probability Buckets
    df_raw = pd.DataFrame(engine.trades_data)
    buckets = [0.52, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 1.0]
    bucket_results = []
    for i in range(len(buckets)-1):
        low, high = buckets[i], buckets[i+1]
        subset = df_raw[(df_raw['probability'] >= low) & (df_raw['probability'] < high)]
        if len(subset) == 0: continue

        wins = subset[subset['outcome'] == 'TARGET_HIT']
        wr = (len(wins) / len(subset)) * 100
        avg_ret = subset['profit_pct'].mean()

        bucket_results.append({
            "bucket": f"{low:.2f}-{high:.2f}",
            "count": len(subset),
            "win_rate": wr,
            "avg_return": avg_ret
        })
    pd.DataFrame(bucket_results).to_csv('data/results/step4_3/probability_buckets.csv', index=False)

    # 2. Threshold Sensitivity
    thresholds = [0.52, 0.55, 0.58, 0.60, 0.62, 0.65, 0.70]
    thresh_res = []
    for t in thresholds:
        # Filter trades_data before simulation
        original_trades = engine.trades_data
        engine.trades_data = [tr for tr in original_trades if tr['probability'] >= t]

        e_df, t_df = engine.run_simulation()

        thresh_res.append({
            "threshold": t,
            "trade_count": len(t_df),
            "win_rate": (t_df['pnl'] > 0).mean() * 100 if len(t_df) > 0 else 0,
            "total_return": (e_df['equity'].iloc[-1] / 1000000 - 1) * 100,
            "max_drawdown": ((e_df['equity'] - e_df['equity'].cummax()) / e_df['equity'].cummax()).min() * 100
        })
        engine.trades_data = original_trades # Restore
    pd.DataFrame(thresh_res).to_csv('data/results/step4_3/threshold_sensitivity.csv', index=False)

    # 3. Long vs Short
    longs = df_raw[df_raw['direction'] == 'LONG']
    shorts = df_raw[df_raw['direction'] == 'SHORT']

    ls_report = f"""# TradeMind AI - Step 4.3 Long/Short Robustness

| Side | Trades | Win Rate | Avg Return |
| :--- | :--- | :--- | :--- |
| **LONG** | {len(longs)} | {(longs['outcome'] == 'TARGET_HIT').mean()*100:.2f}% | {longs['profit_pct'].mean():.4f}% |
| **SHORT** | {len(shorts)} | {(shorts['outcome'] == 'TARGET_HIT').mean()*100:.2f}% | {shorts['profit_pct'].mean():.4f}% |
"""
    with open('docs/step4_3/LONG_SHORT_ROBUSTNESS.md', 'w') as f:
        f.write(ls_report)

    # 4. Gap Robustness
    # Needs portfolio_trades.csv to see actual gap fills
    t_df_verified = pd.read_csv('data/results/portfolio_trades.csv')
    gaps = t_df_verified[t_df_verified['entry_execution_type'] == 'FAVORABLE_GAP']
    normals = t_df_verified[t_df_verified['entry_execution_type'] == 'NORMAL']

    gap_report = f"""# TradeMind AI - Step 4.3 Gap Robustness

| Type | Trades | Win Rate | Avg Return |
| :--- | :--- | :--- | :--- |
| **Normal** | {len(normals)} | {(normals['pnl'] > 0).mean()*100:.2f}% | {normals['return_pct'].mean():.4f}% |
| **Favorable Gap** | {len(gaps)} | {(gaps['pnl'] > 0).mean()*100:.2f}% | {gaps['return_pct'].mean():.4f}% |
"""
    with open('docs/step4_3/GAP_ROBUSTNESS.md', 'w') as f:
        f.write(gap_report)

    print("Robustness suite partial completion (Phases 10, 11, 15, 16).")

if __name__ == "__main__":
    run_robustness()
