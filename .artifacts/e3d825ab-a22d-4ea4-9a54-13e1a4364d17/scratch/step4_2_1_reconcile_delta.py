import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')

    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    # Let's check a specific date: 2020-03-23
    target_date = pd.to_datetime('2020-03-23')

    day_trades = t_df[t_df['exit_date'] == target_date]
    day_equity = e_df[e_df['date'] == target_date].iloc[0]
    prev_equity = e_df[e_df['date'] < target_date].iloc[-1]

    print(f"--- RECONCILIATION FOR {target_date} ---")
    print(f"Reported Equity: {day_equity['equity']:,.2f}")
    print(f"Prev Day Equity: {prev_equity['equity']:,.2f}")
    print(f"Equity Delta: {day_equity['equity'] - prev_equity['equity']:,.2f}")

    print(f"\nExiting Trades PnL: {day_trades['pnl'].sum():,.2f}")
    print(f"Exiting Trades Costs: {day_trades['costs'].sum():,.2f}")

    # Check if there are entries today
    # We don't have entry events in CSV, but we can check entry_date
    entries_today = t_df[t_df['entry_date'] == target_date]
    print(f"New Entries today: {len(entries_today)}")

    # If the engine is correct, Delta = Realized_PnL + Unrealized_Change.
    # If we have a -211k difference between ledger and equity, maybe it's in the unrealized?
    # Or maybe it's in the cash calculation.

    # Let's look at the cash.
    print(f"\nReported Cash: {day_equity['cash']:,.2f}")
    print(f"Prev Day Cash: {prev_equity['cash']:,.2f}")
    print(f"Cash Delta: {day_equity['cash'] - prev_equity['cash']:,.2f}")

if __name__ == "__main__":
    run()
