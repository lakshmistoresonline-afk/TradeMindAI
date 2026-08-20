import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')

    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    # Calculate daily realized net pnl
    daily_pnl = t_df.groupby('exit_date')['pnl'].sum().reset_index()

    # Calculate daily costs
    daily_costs = t_df.groupby('exit_date')['costs'].sum().reset_index()

    # Calculate daily entries (we don't have entry costs directly in CSV, let's assume they were paid)
    # This is tricky because ledger has 'costs' as total.
    # Let's just use the equity delta.

    e_df['equity_delta'] = e_df['equity'].diff().fillna(0)

    # Merge
    recon = pd.merge(e_df, daily_pnl, left_on='date', right_on='exit_date', how='left').fillna(0)

    # Cumulative realized PnL
    recon['cum_realized'] = recon['pnl'].cumsum()
    recon['expected_equity'] = 1000000.0 + recon['cum_realized']

    # For days with no positions, difference should be zero.
    recon['diff'] = recon['equity'] - recon['expected_equity']

    no_pos = recon[recon['pos_count'] == 0].copy()
    no_pos['diff_abs'] = no_pos['diff'].abs()

    divergence = no_pos[no_pos['diff_abs'] > 1.0]

    if not divergence.empty:
        print(f"First Divergence on Zero-Position Day:")
        print(divergence.iloc[0])
        print(f"\nTotal zero-position days with divergence: {len(divergence)}")
    else:
        print("No divergence found on zero-position days.")

    recon.to_csv('docs/STEP4.2_DAILY_LEDGER_FORENSIC.csv', index=False)

if __name__ == "__main__":
    run()
