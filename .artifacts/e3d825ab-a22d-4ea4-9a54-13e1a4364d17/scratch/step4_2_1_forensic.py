import pandas as pd
import numpy as np

def run_forensic():
    trades_path = 'data/results/portfolio_trades.csv'
    equity_path = 'data/results/portfolio_daily_equity.csv'

    t_df = pd.read_csv(trades_path)
    e_df = pd.read_csv(equity_path)

    starting_capital = 1000000.0

    # 1. Trade Ledger Reconstruction
    # In portfolio_trades.csv, does 'pnl' include costs?
    # Based on the code: pnl = (exit-entry)*qty - costs.
    # User's 'Gross P&L' might be pnl + costs.

    total_pnl = t_df['pnl'].sum()
    total_costs = t_df['costs'].sum()

    expected_final_equity = starting_capital + total_pnl
    reported_final_equity = e_df['equity'].iloc[-1]

    print(f"--- TRADE LEDGER ---")
    print(f"Total Net PnL (from CSV 'pnl' column): {total_pnl:,.2f}")
    print(f"Total Costs (from CSV 'costs' column): {total_costs:,.2f}")
    print(f"Expected Final Equity (Start + Net PnL): {expected_final_equity:,.2f}")
    print(f"Reported Final Equity: {reported_final_equity:,.2f}")
    print(f"Difference: {reported_final_equity - expected_final_equity:,.2f}")

    # 2. Daily Reconciliation
    # We need to see how daily equity changes relative to exits.
    e_df['date'] = pd.to_datetime(e_df['date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])

    # Group trades by exit date
    daily_trades = t_df.groupby('exit_date').agg({
        'pnl': 'sum',
        'costs': 'sum'
    }).reset_index()

    # Merge with equity
    e_df['equity_diff'] = e_df['equity'].diff().fillna(0)

    recon = pd.merge(e_df, daily_trades, left_on='date', right_on='exit_date', how='left').fillna(0)

    # The 'expected' equity change for a day with MTM should be:
    # Change = Realized PnL (from trades exiting today) + Change in Unrealized PnL of open positions.
    # This is hard to reconstruct without raw price data, but we can look for large jumps.

    recon['cumulative_pnl'] = recon['pnl'].cumsum()
    recon['expected_equity_static'] = starting_capital + recon['cumulative_pnl']

    # Find first divergence where reported equity differs significantly from start + cum_pnl (ignoring unrealized)
    # Actually, let's just find the discrepancy between daily delta and pnl.

    recon.to_csv('docs/STEP4.2_DAILY_LEDGER_FORENSIC.csv', index=False)

    print("\n--- FIRST DIVERGENCE ---")
    # A simple check: final cash + locked value + unrealized should equal equity.
    # We don't have that info in the CSV, but we can check if the final difference matches something.

    diff = reported_final_equity - expected_final_equity
    print(f"Unexplained surplus: {diff:,.2f}")

if __name__ == "__main__":
    run_forensic()
