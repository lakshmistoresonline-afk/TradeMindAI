import os
import sys
import pandas as pd
import numpy as np
import json

def calculate_stats(results):
    df = pd.DataFrame(results)
    if df.empty: return {}

    wins = len(df[df['outcome'] == 'TARGET_HIT'])
    losses = len(df[df['outcome'] == 'STOP_LOSS'])
    total = len(df)

    # Calculate Max Drawdown
    cum_returns = (1 + df['profit_pct']/100).cumprod()
    peak = cum_returns.expanding().max()
    dd = (cum_returns / peak - 1) * 100

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": (wins / total) * 100 if total > 0 else 0,
        "avg_return": df['profit_pct'].mean(),
        "total_return": df['profit_pct'].sum(),
        "max_drawdown": dd.min()
    }

def run_scenarios():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    with open(results_path, 'r') as f:
        data = json.load(f)

    results = data['results']

    # SCENARIO A: Current (already in data)
    stats_a = calculate_stats(results)

    # SCENARIO B: Corrected (Enforce 3% Stop for EXPIRED if they crossed it)
    results_b = []
    for t in results:
        new_t = t.copy()
        if t['outcome'] == 'EXPIRED':
            # From forensic audit, we know ALL 322 crossed the stop.
            # However, we should also fix the profit_pct.
            # If we assume they hit the 3% stop:
            new_t['outcome'] = 'STOP_LOSS'
            new_t['profit_pct'] = -3.0
            new_t['exit'] = t['stop']
        results_b.append(new_t)
    stats_b = calculate_stats(results_b)

    # SCENARIO C: Corrected + Corporate Action Safe
    # We remove the 4 trades with huge gaps if they were due to adjustments
    # (Actually we just filter trades where raw_loss > 50% as suspicious CA artifacts)
    # But for now, let's just use the corrected logic and see.
    results_c = []
    for t in results_b:
        # Check for extreme profit (e.g. > 100% or < -100%) which shouldn't happen with 3% stop
        if abs(t['profit_pct']) > 50:
            continue
        results_c.append(t)
    stats_c = calculate_stats(results_c)

    print("SCENARIO A (Current):")
    print(json.dumps(stats_a, indent=2))
    print("\nSCENARIO B (Corrected Expiry/Stop):")
    print(json.dumps(stats_b, indent=2))
    print("\nSCENARIO C (Corrected + CA Filter):")
    print(json.dumps(stats_c, indent=2))

if __name__ == "__main__":
    run_scenarios()
