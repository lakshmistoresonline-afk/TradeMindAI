import pandas as pd
import numpy as np
import os

def independent_verify():
    print("--- INDEPENDENT STEP 4.4.1 VERIFICATION ---")
    data_dir = "data/results/step4_4_1"
    trades_path = os.path.join(data_dir, "wf_portfolio_trades.csv")
    equity_path = os.path.join(data_dir, "wf_portfolio_equity.csv")

    if not os.path.exists(trades_path) or not os.path.exists(equity_path):
        print("Missing data files.")
        return

    t_df = pd.read_csv(trades_path)
    e_df = pd.read_csv(equity_path)

    # 1. Trade Count
    trade_count = len(t_df)
    print(f"Total Trades: {trade_count}")

    # 2. PnL Sum
    net_pnl_sum = t_df['pnl'].sum()
    print(f"Sum of Ledger Net PnL: {net_pnl_sum:,.2f}")

    # 3. Final Equity Reconciliation
    starting_capital = 1000000.0
    final_equity = e_df['equity'].iloc[-1]
    expected_final = starting_capital + net_pnl_sum

    print(f"Starting Capital: {starting_capital:,.2f}")
    print(f"Expected Final Equity: {expected_final:,.2f}")
    print(f"Reported Final Equity: {final_equity:,.2f}")

    discrepancy = abs(expected_final - final_equity)
    print(f"Discrepancy: {discrepancy:,.6f}")

    assert discrepancy < 0.01, f"Accounting Reconciliation Failed! Diff: {discrepancy}"
    print("PASS: Accounting Reconciliation verified within ₹0.01.")

    # 4. Duplicate Check
    dupes = t_df.duplicated(subset=['symbol', 'signal_date']).sum()
    print(f"Duplicate trades (symbol + signal_date): {dupes}")
    assert dupes == 0, "Duplicate trades found in ledger!"
    print("PASS: No duplicate trades found.")

if __name__ == "__main__":
    independent_verify()
