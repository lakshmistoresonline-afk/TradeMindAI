import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])

    target_date = pd.to_datetime('2020-03-23')
    day_trades = t_df[t_df['exit_date'] == target_date]

    print(f"Trades exiting on {target_date}:")
    print(day_trades[['symbol', 'direction', 'entry_price', 'exit_price', 'quantity', 'pnl', 'costs']])

if __name__ == "__main__":
    run()
