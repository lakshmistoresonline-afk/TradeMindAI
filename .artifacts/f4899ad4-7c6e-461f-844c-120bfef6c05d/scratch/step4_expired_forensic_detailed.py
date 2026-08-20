
import json
import pandas as pd
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def forensic():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    with open(results_path, 'r') as f:
        data = json.load(f)

    expired = [r for r in data['results'] if r['outcome'] == 'EXPIRED']
    df = pd.DataFrame(expired)

    # Analyze holding periods of EXPIRED
    print("--- EXPIRED TRADES HOLDING PERIODS ---")
    print(df['holding_period'].value_counts())

    # Identify non-triggered trades
    non_triggered = df[df['holding_period'] == 1].copy()
    print(f"\nNon-triggered EXPIRED trades: {len(non_triggered)}")

    # Calculate impact on stats
    total_trades = len(data['results'])
    wins = len([r for r in data['results'] if r['outcome'] == 'TARGET_HIT'])
    losses = len([r for r in data['results'] if r['outcome'] == 'STOP_LOSS'])

    # Original stats
    avg_ret_orig = sum(r['profit_pct'] for r in data['results']) / total_trades

    # Filtered stats (Exclude non-triggered)
    triggered_results = [r for r in data['results'] if not (r['outcome'] == 'EXPIRED' and r['holding_period'] == 1)]
    total_triggered = len(triggered_results)
    avg_ret_filt = sum(r['profit_pct'] for r in triggered_results) / total_triggered

    print(f"\nIMPACT ANALYSIS:")
    print(f"Original Avg Return: {avg_ret_orig:.4f}%")
    print(f"Filtered Avg Return: {avg_ret_filt:.4f}%")
    print(f"Alpha Leakage: {avg_ret_filt - avg_ret_orig:.4f}%")

    # Save forensic CSV
    df.to_csv('docs/STEP4_EXPIRED_FORENSIC.csv', index=False)
    print("\nSaved docs/STEP4_EXPIRED_FORENSIC.csv")

if __name__ == "__main__":
    forensic()
