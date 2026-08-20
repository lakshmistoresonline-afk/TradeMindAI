
import json
import pandas as pd
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def forensic():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    if not os.path.exists(results_path):
        print("Results file not found.")
        return

    with open(results_path, 'r') as f:
        data = json.load(f)

    expired = [r for r in data['results'] if r['outcome'] == 'EXPIRED']
    print(f"Total EXPIRED trades: {len(expired)}")

    df_expired = pd.DataFrame(expired)

    # Identify extreme losses
    extreme = df_expired[df_expired['profit_pct'] < -20].copy()
    print(f"Extreme losses (< -20%): {len(extreme)}")

    # Save forensic CSV
    df_expired.to_csv('docs/STEP4_EXPIRED_FORENSIC.csv', index=False)
    print("Saved docs/STEP4_EXPIRED_FORENSIC.csv")

    # Sample extreme trade investigation
    if not extreme.empty:
        sample = extreme.iloc[0]
        print(f"\nInvestigating sample extreme trade: {sample['symbol']} on {sample['signal_date']}")
        print(sample)

        # Check database for this symbol around those dates
        db_path = "backend/local_operational.db"
        conn = sqlite3.connect(db_path)

        sig_date = sample['signal_date'].split('T')[0]
        query = f"SELECT * FROM historical_prices WHERE symbol = '{sample['symbol']}' AND date >= '{sig_date}' LIMIT 50"
        df_hist = pd.read_sql_query(query, conn)
        print("\nHistorical Data around signal:")
        print(df_hist.head(10))
        conn.close()

if __name__ == "__main__":
    forensic()
