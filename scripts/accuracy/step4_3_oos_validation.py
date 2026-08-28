import json
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def run_oos_validation():
    results_path = 'data/results/portfolio_trades.csv'
    if not os.path.exists(results_path):
        print("Portfolio trades ledger missing.")
        return

    df = pd.read_csv(results_path)
    df['entry_dt'] = pd.to_datetime(df['entry_date'])
    df = df.sort_values('entry_dt')

    total_trades = len(df)
    is_split = int(total_trades * 0.6)
    val_split = int(total_trades * 0.8)

    is_df = df.iloc[:is_split]
    val_df = df.iloc[is_split:val_split]
    oos_df = df.iloc[val_split:]

    boundaries = {
        "in_sample": {"start": is_df['entry_dt'].min().isoformat(), "end": is_df['entry_dt'].max().isoformat(), "trades": len(is_df)},
        "validation": {"start": val_df['entry_dt'].min().isoformat(), "end": val_df['entry_dt'].max().isoformat(), "trades": len(val_df)},
        "out_sample": {"start": oos_df['entry_dt'].min().isoformat(), "end": oos_df['entry_dt'].max().isoformat(), "trades": len(oos_df)}
    }

    with open('data/results/step4_3/period_boundaries.json', 'w') as f:
        json.dump(boundaries, f, indent=4)

    def calc_metrics(subset):
        if len(subset) == 0: return {}
        wins = subset[subset['net_pnl'] > 0]
        losses = subset[subset['net_pnl'] <= 0]

        total_pnl = subset['net_pnl'].sum()
        avg_ret = subset['return_pct'].mean()
        wr = (len(wins) / len(subset)) * 100
        pf = abs(wins['net_pnl'].sum() / losses['net_pnl'].sum()) if len(losses) > 0 else 0

        return {
            "trades": len(subset),
            "win_rate": wr,
            "avg_return": avg_ret,
            "total_pnl": total_pnl,
            "profit_factor": pf
        }

    is_metrics = calc_metrics(is_df)
    val_metrics = calc_metrics(val_df)
    oos_metrics = calc_metrics(oos_df)

    report_md = f"""# TradeMind AI - Step 4.3 Out-of-Sample Report

## Dataset Segmentation
| Split | Start | End | Trades |
| :--- | :--- | :--- | :--- |
| **In-Sample (60%)** | {boundaries['in_sample']['start']} | {boundaries['in_sample']['end']} | {boundaries['in_sample']['trades']} |
| **Validation (20%)** | {boundaries['validation']['start']} | {boundaries['validation']['end']} | {boundaries['validation']['trades']} |
| **Out-of-Sample (20%)** | {boundaries['out_sample']['start']} | {boundaries['out_sample']['end']} | {boundaries['out_sample']['trades']} |

## Performance Comparison
| Metric | In-Sample | Validation | Out-of-Sample |
| :--- | :--- | :--- | :--- |
| **Win Rate** | {is_metrics['win_rate']:.2f}% | {val_metrics['win_rate']:.2f}% | {oos_metrics['win_rate']:.2f}% |
| **Avg Return** | {is_metrics['avg_return']:.4f}% | {val_metrics['avg_return']:.4f}% | {oos_metrics['avg_return']:.4f}% |
| **Profit Factor** | {is_metrics['profit_factor']:.4f} | {val_metrics['profit_factor']:.4f} | {oos_metrics['profit_factor']:.4f} |
| **Total Net PnL** | {is_metrics['total_pnl']:,.2f} | {val_metrics['total_pnl']:,.2f} | {oos_metrics['total_pnl']:,.2f} |

## Degradation Analysis
- **OOS / IS Profit Factor Ratio**: {oos_metrics['profit_factor'] / is_metrics['profit_factor']:.2f}
- **OOS / IS Avg Return Ratio**: {oos_metrics['avg_return'] / is_metrics['avg_return']:.2f}

## Conclusion
{"PASS: Strategy maintains positive edge in OOS." if oos_metrics['avg_return'] > 0 else "FAIL: Strategy degrades to negative return in OOS."}
"""
    with open('docs/step4_3/OOS_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report_md)

    oos_df.to_csv('data/results/step4_3/oos_trades.csv', index=False)
    print("Generated docs/step4_3/OOS_REPORT.md")

if __name__ == "__main__":
    run_oos_validation()
