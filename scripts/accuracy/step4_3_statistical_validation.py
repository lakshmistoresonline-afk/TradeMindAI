import pandas as pd
import numpy as np
import os
import sys

def run_statistical_validation():
    trades_path = 'data/results/portfolio_trades.csv'
    if not os.path.exists(trades_path):
        print("Ledger missing.")
        return

    df = pd.read_csv(trades_path)

    # 1. Monte Carlo (Trade Order Shuffle)
    # Since we don't have full equity curve simulation here, we'll randomize sequence of realized PnL
    returns = df['net_pnl'].tolist()
    starting_cap = 1000000.0

    n_sims = 10000
    mc_results = []

    for _ in range(n_sims):
        shuffled = np.random.permutation(returns)
        equity_curve = starting_cap + np.cumsum(shuffled)
        final_ret = (equity_curve[-1] / starting_cap - 1) * 100
        # Simple DD on realized sequence
        peak = np.maximum.accumulate(equity_curve)
        dd = (equity_curve - peak) / peak * 100
        mc_results.append({
            "final_return": final_ret,
            "max_drawdown": dd.min()
        })

    mc_df = pd.DataFrame(mc_results)

    # 2. Bootstrap (Confidence Intervals)
    n_boot = 10000
    boot_wr = []
    boot_avg_ret = []

    for _ in range(n_boot):
        sample = df.sample(frac=1, replace=True)
        boot_wr.append((sample['pnl'] > 0).mean() * 100)
        boot_avg_ret.append(sample['return_pct'].mean())

    ci_wr = np.percentile(boot_wr, [2.5, 97.5])
    ci_avg = np.percentile(boot_avg_ret, [2.5, 97.5])

    report_md = f"""# TradeMind AI - Step 4.3 Statistical Validation

## Monte Carlo Results (10,000 Shuffles)
| Percentile | Final Return | Max Drawdown |
| :--- | :--- | :--- |
| **5th** | {np.percentile(mc_df['final_return'], 5):.2f}% | {np.percentile(mc_df['max_drawdown'], 5):.2f}% |
| **Median** | {np.percentile(mc_df['final_return'], 50):.2f}% | {np.percentile(mc_df['max_drawdown'], 50):.2f}% |
| **95th** | {np.percentile(mc_df['final_return'], 95):.2f}% | {np.percentile(mc_df['max_drawdown'], 95):.2f}% |

## Bootstrap Confidence Intervals (10,000 Samples)
- **Win Rate (95% CI)**: {ci_wr[0]:.2f}% to {ci_wr[1]:.2f}%
- **Avg Return (95% CI)**: {ci_avg[0]:.4f}% to {ci_avg[1]:.4f}%

## MAE/MFE Analysis
- **Avg Maximum Adverse Excursion (MAE)**: {df['risk_amount'].mean() / df['position_value'].mean() * 100:.2f}% (Approx)
- **Avg Maximum Favorable Excursion (MFE)**: {df['gross_pnl'].clip(lower=0).mean() / df['position_value'].mean() * 100:.2f}% (Approx)

## Conclusion
The Monte Carlo median drawdown of {np.percentile(mc_df['max_drawdown'], 50):.2f}% provides a robust baseline for sequence risk.
"""
    with open('docs/step4_3/MONTE_CARLO_REPORT.md', 'w') as f:
        f.write(report_md)

    mc_df.to_csv('data/results/step4_3/monte_carlo_results.csv', index=False)
    print("Generated docs/step4_3/MONTE_CARLO_REPORT.md")

if __name__ == "__main__":
    run_statistical_validation()
