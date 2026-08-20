import pandas as pd
import numpy as np

def run_audit():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')

    # We need to simulate the portfolio state exactly as the engine does to find the leak.
    # Since we don't have the signals that were REJECTED, we can't fully simulate.
    # But we can check the trades that DID execute.

    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    # Reconstruct cash flow from executed trades
    starting_capital = 1000000.0
    cash = starting_capital

    # We need a chronological list of events for THESE trades
    events = []
    for i, row in t_df.iterrows():
        # Entry event
        # Note: We need to know entry_costs. In CSV, 'costs' is total costs.
        # How to split entry and exit costs?
        # Based on code, they are likely equal if slippage is 0 and prices are similar.
        # But let's look at the code: entry_costs is calculated at entry_price, exit_costs at exit_price.
        # We can approximate or just use the ledger's 'costs' at exit.
        # Wait, the code subtracts entry_costs from cash at ENTRY.
        # So we NEED entry_costs.

        # Let's assume entry_costs = costs / 2 for now, or better, re-calculate them.
        # Actually, let's just look at the reported cash in e_df.
        pass

    # Better approach:
    # On any day, Equity = Cash + Locked_Value + Unrealized_PnL.
    # Let's pick a day early on.

    first_days = e_df.head(20)
    print("--- EARLY DAYS EQUITY ---")
    print(first_days[['date', 'equity', 'cash', 'pos_count']])

    # Find first trade
    first_trade = t_df.sort_values('entry_date').iloc[0]
    print(f"\nFirst Trade: {first_trade['symbol']} on {first_trade['entry_date']}")

    # Check equity on first trade entry day
    entry_day_equity = e_df[e_df['date'] == first_trade['entry_date']]
    print(f"Equity on entry day: \n{entry_day_equity}")

if __name__ == "__main__":
    run_audit()
