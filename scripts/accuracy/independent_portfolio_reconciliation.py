import pandas as pd
import numpy as np
import os
import yaml

def reconcile():
    trades_path = 'data/results/portfolio_trades.csv'
    equity_path = 'data/results/portfolio_daily_equity.csv'
    config_path = 'config/portfolio_backtest.yaml'

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    t_df = pd.read_csv(trades_path)
    e_df = pd.read_csv(equity_path)

    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    starting_capital = 1000000.0

    print("--- INDEPENDENT LEDGER AUDIT ---")

    # 1. Formula Check
    def calc_pnl(row):
        gross = 0
        if row['direction'] == 'LONG':
            gross = (row['exit_price'] - row['entry_price']) * row['quantity']
        else:
            gross = (row['entry_price'] - row['exit_price']) * row['quantity']
        return gross - row['costs']

    t_df['calc_pnl'] = t_df.apply(calc_pnl, axis=1)
    t_df['pnl_diff'] = (t_df['pnl'] - t_df['calc_pnl']).abs()

    max_pnl_diff = t_df['pnl_diff'].max()
    print(f"Max PnL Formula Discrepancy: {max_pnl_diff:.6f}")

    if max_pnl_diff > 0.01:
        print("FAIL: Ledger PnL formula is inconsistent with entry/exit/qty/costs.")
    else:
        print("PASS: Ledger PnL formula is consistent.")

    # 2. Total Sums
    sum_pnl = t_df['pnl'].sum()
    sum_costs = t_df['costs'].sum()

    t_df['gross'] = t_df.apply(lambda r: (r['exit_price'] - r['entry_price']) * r['quantity'] if r['direction'] == 'LONG' else (r['entry_price'] - r['exit_price']) * r['quantity'], axis=1)
    sum_gross = t_df['gross'].sum()

    print(f"\nSum Gross PnL: {sum_gross:,.2f}")
    print(f"Sum Costs: {sum_costs:,.2f}")
    print(f"Sum PnL (Net): {sum_pnl:,.2f}")
    print(f"Gross - Costs: {sum_gross - sum_costs:,.2f}")

    assert abs(sum_pnl - (sum_gross - sum_costs)) < 0.01, "Ledger internal PnL sum mismatch!"

    # 3. Daily Equity vs Cash Reconciliation
    # On zero-pos days, Equity must equal Cash.
    e_df['equity_cash_diff'] = (e_df['equity'] - e_df['cash']).abs()
    zero_pos = e_df[e_df['pos_count'] == 0]
    if not zero_pos.empty:
        max_zero_diff = zero_pos['equity_cash_diff'].max()
        print(f"\nMax Equity-Cash Diff on Zero-Pos Days: {max_zero_diff:.6f}")
        assert max_zero_diff < 0.01, f"Equity must equal Cash when no positions are held. Found diff: {max_zero_diff}"

    # 4. Independent Verification of Equity Delta
    print("\n--- EQUITY DELTA VERIFICATION ---")
    daily_realized = t_df.groupby('exit_date')['pnl'].sum().reset_index()
    daily_realized.columns = ['date', 'realized_pnl']
    daily_realized['date'] = pd.to_datetime(daily_realized['date'])

    # Also sum costs and gross
    daily_costs = t_df.groupby('exit_date')['costs'].sum().reset_index()
    daily_costs.columns = ['date', 'ledger_costs']
    daily_costs['date'] = pd.to_datetime(daily_costs['date'])

    recon = pd.merge(e_df, daily_realized, on='date', how='left').fillna(0)
    recon = pd.merge(recon, daily_costs, on='date', how='left').fillna(0)

    recon['cash_delta'] = recon['cash'].diff().fillna(0)

    # Line-by-Line Audit
    recon['cum_realized'] = recon['realized_pnl'].cumsum()
    recon['expected_equity_if_no_pos'] = starting_capital + recon['cum_realized']

    # Audit logic: Equity - Expected Equity should represent (Unrealized PnL + Value of Locked Cash)
    recon['audit_diff'] = recon['equity'] - recon['expected_equity_if_no_pos']

    print("\nAudit Trail (Last 20 Days):")
    print(recon[['date', 'equity', 'cash', 'pos_count', 'realized_pnl', 'expected_equity_if_no_pos', 'audit_diff']].tail(20).to_string())

    zero_pos_recon = recon[recon['pos_count'] == 0].copy()
    if not zero_pos_recon.empty:
        zero_pos_recon['diff'] = (zero_pos_recon['equity'] - zero_pos_recon['expected_equity_if_no_pos']).abs()

        # Debug first divergence
        divergence = zero_pos_recon[zero_pos_recon['diff'] > 0.01]
        if not divergence.empty:
            first = divergence.iloc[0]
            print(f"\n--- DIVERGENCE DEBUG ({first['date']}) ---")
            print(f"Equity: {first['equity']:,.2f}")
            print(f"Expected: {first['expected_equity_if_no_pos']:,.2f}")
            print(f"Diff: {first['diff']:,.2f}")
            print(f"Cumulative Realized PnL: {first['cum_realized']:,.2f}")

            # Look at trades on that day
            day_trades = t_df[t_df['exit_date'] == str(first['date']).split(' ')[0] + 'T00:00:00']
            print(f"Trades Exiting on this day: {len(day_trades)}")
            if not day_trades.empty:
                print(day_trades[['symbol', 'direction', 'pnl', 'costs']].to_string())

        max_diff_row = zero_pos_recon.loc[zero_pos_recon['diff'].idxmax()]
        print(f"\nFinal Check: Max diff on zero-pos checkpoints = {max_diff_row['diff']:.6f}")
        assert max_diff_row['diff'] < 0.01, f"Portfolio reconciliation failed! Diff: {max_diff_row['diff']}"
        print("PASS: Portfolio equity matches realized PnL on all zero-position checkpoints.")


if __name__ == "__main__":
    reconcile()
