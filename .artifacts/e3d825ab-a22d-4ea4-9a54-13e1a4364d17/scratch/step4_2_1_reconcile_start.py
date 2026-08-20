import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')

    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    # Sort trades by exit
    t_df = t_df.sort_values('exit_date')

    first_exit_date = t_df.iloc[0]['exit_date']
    print(f"First Exit Date: {first_exit_date}")

    # Cumulative pnl up to first exit date
    pnl_today = t_df[t_df['exit_date'] == first_exit_date]['pnl'].sum()
    print(f"PnL exiting today: {pnl_today}")

    equity_today = e_df[e_df['date'] == first_exit_date].iloc[0]
    prev_equity = e_df[e_df['date'] < first_exit_date].iloc[-1]

    print(f"Prev Equity: {prev_equity['equity']}")
    print(f"Reported Equity Today: {equity_today['equity']}")
    print(f"Equity Delta: {equity_today['equity'] - prev_equity['equity']}")

if __name__ == "__main__":
    run()
