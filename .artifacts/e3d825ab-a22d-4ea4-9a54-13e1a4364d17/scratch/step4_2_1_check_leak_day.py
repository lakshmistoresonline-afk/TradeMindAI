import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')
    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    target_date = pd.to_datetime('2026-08-03')

    day_trades = t_df[t_df['exit_date'] == target_date]
    print(f"Trades exiting on {target_date}:")
    print(day_trades)

    day_equity = e_df[e_df['date'] == target_date]
    print(f"\nEquity on {target_date}:")
    print(day_equity)

    prev_date = e_df[e_df['date'] < target_date].iloc[-1]['date']
    prev_equity = e_df[e_df['date'] == prev_date]
    print(f"\nEquity on {prev_date}:")
    print(prev_equity)

if __name__ == "__main__":
    run()
