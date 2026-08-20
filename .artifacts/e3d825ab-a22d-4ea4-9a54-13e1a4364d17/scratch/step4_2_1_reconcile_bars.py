import pandas as pd
import numpy as np

def run_reconcile():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')

    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    starting_capital = 1000000.0

    # We want to check the equation:
    # Equity(t) = starting_capital + Cumulative_Realized_Net_PnL(t) + Unrealized_Net_PnL(t)
    # Wait, Unrealized_Net_PnL(t) should be Gross_Unrealized - entry_costs_of_open.

    # Let's simplify: check days where pos_count == 0.
    # On those days, Equity should be exactly starting_capital + cumulative_realized_pnl.

    no_pos_days = e_df[e_df['pos_count'] == 0].copy()

    # Get cumulative realized pnl up to each date
    # A trade is realized on its exit_date.
    t_df = t_df.sort_values('exit_date')

    results = []
    for i, row in no_pos_days.iterrows():
        date = row['date']
        realized_until_now = t_df[t_df['exit_date'] <= date]['pnl'].sum()
        expected_equity = starting_capital + realized_until_now
        diff = row['equity'] - expected_equity
        results.append({
            'date': date,
            'reported_equity': row['equity'],
            'expected_equity': expected_equity,
            'difference': diff,
            'cum_realized': realized_until_now
        })

    res_df = pd.DataFrame(results)
    print("--- RECONCILIATION ON ZERO-POSITION DAYS ---")
    print(res_df.head(20))
    print("\n--- LAST ZERO-POSITION DAY ---")
    print(res_df.tail(1))

if __name__ == "__main__":
    run_reconcile()
