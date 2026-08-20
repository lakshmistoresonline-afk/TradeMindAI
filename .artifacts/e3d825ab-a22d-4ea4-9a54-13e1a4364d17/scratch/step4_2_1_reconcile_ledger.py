import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')

    t_df['entry_date'] = pd.to_datetime(t_df['entry_date'])
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])

    # We will build a virtual cash ledger based on the trades.
    # Note: t_df ONLY contains executed trades.

    starting_capital = 1000000.0

    # Create events for executed trades
    events = []
    for i, row in t_df.iterrows():
        # Entry cost calculation is hard because we don't have it in CSV.
        # But we can assume it's roughly costs / 2.
        # Wait, the ledger has 'pnl' and 'costs'.
        # pnl = Gross - Costs.
        # So Gross = pnl + costs.
        # Gross = (exit - entry) * qty.
        # costs = entry_costs + exit_costs.

        # Let's try to find a day where reported equity diverged.
        pass

    # Actually, I'll calculate the 'expected_equity' at every day based on the ledger.
    # Expected_Equity(t) = 1M + sum(pnl of trades exited until t) - sum(entry_costs of trades open at t) + sum(unrealized gross pnl of trades open at t).
    # This is also complex.

    # Let's check the very first trade.
    first_trade = t_df.sort_values('entry_date').iloc[0]
    print(f"First trade: {first_trade['symbol']} | Entry: {first_trade['entry_date']} | Exit: {first_trade['exit_date']}")
    print(f"PnL: {first_trade['pnl']} | Costs: {first_trade['costs']}")

    # Check equity on entry day
    entry_day = e_df[e_df['date'] == first_trade['entry_date']].iloc[0]
    print(f"Equity on Entry Day ({first_trade['entry_date']}): {entry_day['equity']}")
    print(f"Cash on Entry Day: {entry_day['cash']}")

    # If this was the ONLY trade:
    # cash = 1M - (entry*qty + e_costs)
    # equity = cash + entry*qty + 0 = 1M - e_costs.

    expected_entry_equity = 1000000.0 - (first_trade['costs'] / 2) # approx
    print(f"Expected Equity (approx): {expected_entry_equity}")

if __name__ == "__main__":
    run()
