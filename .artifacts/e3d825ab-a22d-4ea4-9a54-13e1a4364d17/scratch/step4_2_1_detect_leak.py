import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    daily_pnl = t_df.groupby('exit_date')['pnl'].sum().reset_index()
    recon = pd.merge(e_df, daily_pnl, left_on='date', right_on='exit_date', how='left').fillna(0)

    # We will track 'Expected Ledger Equity' = 1M + sum(pnl)
    # vs 'Reported Portfolio Equity'.

    recon['ledger_equity'] = 1000000.0 + recon['pnl'].cumsum()

    # The 'leak' on any day with no positions is ledger_equity - reported_equity.
    recon['leak'] = recon['ledger_equity'] - recon['equity']

    no_pos = recon[recon['pos_count'] == 0].copy()
    print("--- LEAK OVER TIME (Zero Pos Days) ---")
    print(no_pos[['date', 'ledger_equity', 'equity', 'leak']].head(10))
    print("...")
    print(no_pos[['date', 'ledger_equity', 'equity', 'leak']].tail(10))

if __name__ == "__main__":
    run()
