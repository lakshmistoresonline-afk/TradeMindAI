import json
import pandas as pd

def run():
    with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
        trades_data = json.load(f)['results']

    t_df = pd.read_csv('data/results/portfolio_trades.csv')

    print(f"Total Signals: {len(trades_data)}")
    print(f"Executed Trades (Ledger): {len(t_df)}")

    # Check for duplicates in ledger
    # Note: we don't have tid in ledger.
    # Let's check symbol + signal_date.

    t_df['key'] = t_df['symbol'] + "_" + t_df['entry_date']
    dupes = t_df[t_df.duplicated('key')]
    print(f"Duplicate trades in ledger (Sym_Date): {len(dupes)}")

if __name__ == "__main__":
    run()
