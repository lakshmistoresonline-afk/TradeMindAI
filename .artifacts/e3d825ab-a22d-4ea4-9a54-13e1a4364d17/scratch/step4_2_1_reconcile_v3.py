import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')

    # Reconstruct the ledger sum
    starting_capital = 1000000.0

    # Ledger PnL is NET of all costs.
    # So Expected_Final = Start + Sum(pnl).
    total_ledger_pnl = t_df['pnl'].sum()
    expected_final = starting_capital + total_ledger_pnl

    # Reported Final Equity
    reported_final = e_df['equity'].iloc[-1]

    print(f"Total Ledger PnL: {total_ledger_pnl:,.2f}")
    print(f"Expected Final Equity (Start + Net PnL): {expected_final:,.2f}")
    print(f"Reported Final Equity: {reported_final:,.2f}")
    print(f"Accounting Difference: {reported_final - expected_final:,.2f}")

if __name__ == "__main__":
    run()
