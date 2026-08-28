import os
import sys
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from scripts.accuracy.portfolio_simulator import PortfolioBacktestEngine

def run_wf_portfolio(input_path: str = "data/results/step4_4_2/walk_forward_trades.json",
                     output_dir: str = "data/results/step4_4_2",
                     docs_dir: str = "docs/step4_4_2"):
    print("--- WALK-FORWARD PORTFOLIO SIMULATION ---")
    config_path = "config/portfolio_backtest.yaml"
    db_path = "backend/local_operational.db"

    if not os.path.exists(input_path):
        print(f"Input {input_path} not found.")
        return

    engine = PortfolioBacktestEngine(config_path, input_path, db_path)
    e_df, t_df = engine.run_simulation()

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    doc_path = Path(docs_dir)
    doc_path.mkdir(parents=True, exist_ok=True)

    final_equity = e_df['equity'].iloc[-1]
    total_trades = len(t_df)
    win_rate = (len(t_df[t_df['pnl'] > 0]) / total_trades) * 100 if total_trades > 0 else 0

    # Save outputs
    e_df.to_csv(out_path / "wf_portfolio_equity.csv", index=False)
    t_df.to_csv(out_path / "wf_portfolio_trades.csv", index=False)

    # Per-window breakdown
    # Mapping window to trades
    with open(input_path, 'r') as f:
        raw_signals = json.load(f)['results']

    # We need to map window_id from raw_signals back to t_df
    # Simple mapping based on symbol and signal_date
    signal_map = {(s['symbol'], s['signal_date']): s['window_id'] for s in raw_signals}
    t_df['window_id'] = t_df.apply(lambda r: signal_map.get((r['symbol'], r['signal_date']), "UNKNOWN"), axis=1)

    window_stats = t_df.groupby('window_id').agg({
        'pnl': 'sum',
        'symbol': 'count',
    }).rename(columns={'symbol': 'trade_count', 'pnl': 'net_pnl'})

    # Win rate per window
    win_rate_per_win = t_df.groupby('window_id').apply(lambda x: (len(x[x['pnl'] > 0]) / len(x)) * 100 if len(x) > 0 else 0)
    window_stats['win_rate'] = win_rate_per_win

    window_stats.to_csv(out_path / "window_performance.csv")

    report_md = f"""# Step 4.4.1 Full NIFTY 200 Walk-Forward Report

## Execution Summary
- **Total Signals Candidate**: {len(raw_signals)}
- **Executed Portfolio Trades**: {total_trades}
- **Final Equity**: ₹{final_equity:,.2f}
- **Total Net PnL**: ₹{final_equity - 1000000:,.2f}
- **Portfolio Win Rate**: {win_rate:.2f}%

## Window Performance Breakdown
{window_stats.to_markdown()}

## Conclusion
{"PASS: Walk-forward maintains profitability across the NIFTY 200 universe." if final_equity > 1000000 else "FAIL: Walk-forward results in loss."}
"""
    with open(doc_path / "FULL_NIFTY200_WALK_FORWARD_REPORT.md", 'w', encoding='utf-8') as f:
        f.write(report_md)

    print(f"[SUCCESS] WF Portfolio complete. Final Equity: {final_equity:,.2f}")

if __name__ == "__main__":
    run_wf_portfolio()
