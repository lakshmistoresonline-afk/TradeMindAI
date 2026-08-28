import pandas as pd
import numpy as np
import os

def independent_verify():
    print("--- INDEPENDENT STEP 4.4.2 VERIFICATION ---")
    data_dir = "data/results/step4_4_2"
    trades_path = os.path.join(data_dir, "wf_portfolio_trades.csv")
    equity_path = os.path.join(data_dir, "wf_portfolio_equity.csv")

    if not os.path.exists(trades_path) or not os.path.exists(equity_path):
        print("Missing data files.")
        return

    t_df = pd.read_csv(trades_path)
    e_df = pd.read_csv(equity_path)

    # 1. Final Equity Reconciliation
    starting_capital = 1000000.0
    sum_pnl = t_df['pnl'].sum()
    reported_final = e_df['equity'].iloc[-1]
    expected_final = starting_capital + sum_pnl

    discrepancy = abs(expected_final - reported_final)
    print(f"Discrepancy: {discrepancy:,.6f}")

    assert discrepancy < 0.01, f"Accounting Reconciliation Failed! Diff: {discrepancy}"
    print("PASS: Accounting Reconciliation verified within ₹0.01.")

    # 2. Duplicate Check
    dupes = t_df.duplicated(subset=['symbol', 'signal_date']).sum()
    assert dupes == 0, f"Found {dupes} duplicate signals in ledger!"
    print("PASS: No duplicate trades found.")

if __name__ == "__main__":
    independent_verify()
