import pandas as pd
import numpy as np
import json
import sqlite3

def forensic_audit():
    trades_path = 'data/results/portfolio_trades.csv'
    equity_path = 'data/results/portfolio_daily_equity.csv'

    t_df = pd.read_csv(trades_path)
    e_df = pd.read_csv(equity_path)

    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    starting_capital = 1000000.0

    # 1. Check sum of pnl
    total_pnl = t_df['pnl'].sum()
    total_costs = t_df['costs'].sum()
    print(f"Ledger PnL Sum: {total_pnl:,.2f}")
    print(f"Ledger Costs Sum: {total_costs:,.2f}")

    # 2. Daily Delta Audit
    # We want to see if daily realized pnl matches daily equity change on no-pos days.
    daily_realized = t_df.groupby('exit_date')['pnl'].sum().reset_index()

    merged = pd.merge(e_df, daily_realized, left_on='date', right_on='exit_date', how='left').fillna(0)

    merged['expected_realized'] = starting_capital + merged['pnl'].cumsum()
    merged['unaccounted_loss'] = merged['expected_realized'] - merged['equity']

    no_pos = merged[merged['pos_count'] == 0].copy()

    print("\n--- ACCOUNTING LEAKAGE (No positions) ---")
    print(no_pos[['date', 'equity', 'expected_realized', 'unaccounted_loss']].tail(10))

    # Identify the biggest jump in unaccounted loss
    no_pos['leak_delta'] = no_pos['unaccounted_loss'].diff().fillna(0)
    jumps = no_pos[no_pos['leak_delta'].abs() > 100].sort_values('leak_delta', ascending=False)

    print("\n--- MAJOR LEAK JUMPS ---")
    print(jumps[['date', 'leak_delta']].head(10))

if __name__ == "__main__":
    forensic_audit()
