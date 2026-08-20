
import json
import pandas as pd
import numpy as np
import os

def recalculate():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    if not os.path.exists(results_path):
        print("Results file not found.")
        return

    with open(results_path, 'r') as f:
        data = json.load(f)

    results = data['results']
    df = pd.DataFrame(results)

    # 1. SCENARIO A: Current
    print("--- SCENARIO A: CURRENT ---")
    print_stats(df)

    # 2. SCENARIO B: Exclude non-triggered EXPIRED trades
    # We define 'triggered' if it reached TARGET_HIT, STOP_LOSS,
    # or EXPIRED with holding_period > 1 (meaning it became ACTIVE)
    # Wait, holding_period in my script was len(events).
    # If it becomes ACTIVE, it has at least 1 event (ENTRY_TRIGGERED).
    # If it then expires, it has 2 events (ENTRY_TRIGGERED, EXPIRED).
    # So holding_period > 1 means it triggered.

    df_triggered = df[~((df['outcome'] == 'EXPIRED') & (df['holding_period'] == 1))].copy()
    print("\n--- SCENARIO B: TRIGGERED TRADES ONLY ---")
    print_stats(df_triggered)

    # 3. Investigation of EXPIRED trades with extreme losses
    expired_triggered = df[(df['outcome'] == 'EXPIRED') & (df['holding_period'] > 1)]
    print(f"\nExpired but triggered trades: {len(expired_triggered)}")
    if not expired_triggered.empty:
        print(f"Max profit in expired: {expired_triggered['profit_pct'].max():.2f}%")
        print(f"Min profit in expired: {expired_triggered['profit_pct'].min():.2f}%")

def print_stats(df):
    if df.empty: return

    total = len(df)
    wins = len(df[df['outcome'] == 'TARGET_HIT'])
    losses = len(df[df['outcome'] == 'STOP_LOSS'])
    expired = len(df[df['outcome'] == 'EXPIRED'])

    win_rate = (wins / total) * 100
    avg_return = df['profit_pct'].mean()
    total_return = df['profit_pct'].sum()

    print(f"Total Trades: {total}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Avg Return: {avg_return:.4f}%")
    print(f"Total Return: {total_return:.2f}%")
    print(f"TARGET_HIT: {wins} | STOP_LOSS: {losses} | EXPIRED: {expired}")

    # Drawdown
    cum_returns = (1 + df['profit_pct']/100).cumprod()
    peak = cum_returns.expanding().max()
    dd = (cum_returns / peak - 1) * 100
    print(f"Max Drawdown: {dd.min():.2f}%")

if __name__ == "__main__":
    recalculate()
