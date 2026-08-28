import os
import sys
import json
import sqlite3
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def run_symbol_sector_audit():
    print("Running Symbol & Sector Audit...")
    trades_path = "data/results/portfolio_trades.csv"
    if not os.path.exists(trades_path):
        print("Error: portfolio_trades.csv not found.")
        return

    df = pd.read_csv(trades_path)

    # 1. Symbol Robustness
    symbol_stats = df.groupby('symbol').agg({
        'pnl': ['sum', 'count', 'mean'],
        'net_pnl': 'sum' # If available, otherwise use pnl
    })
    symbol_stats.columns = ['total_pnl', 'trade_count', 'avg_pnl', 'net_pnl']
    symbol_stats = symbol_stats.sort_values('total_pnl', ascending=False)

    top_5 = symbol_stats.head(5)['total_pnl'].sum()
    top_10 = symbol_stats.head(10)['total_pnl'].sum()
    top_20 = symbol_stats.head(20)['total_pnl'].sum()
    total_pnl = symbol_stats['total_pnl'].sum()

    concentration = {
        "Top 1": symbol_stats.iloc[0]['total_pnl'] / total_pnl,
        "Top 5": top_5 / total_pnl,
        "Top 10": top_10 / total_pnl,
        "Top 20": top_20 / total_pnl
    }

    # 2. Sector Robustness
    conn = sqlite3.connect("backend/local_operational.db")
    df_sectors = pd.read_sql_query("SELECT symbol, sector FROM stocks", conn)
    conn.close()

    df = pd.merge(df, df_sectors, on='symbol', how='left')
    df['sector'] = df['sector'].fillna("Unknown")

    sector_stats = df.groupby('sector').agg({
        'pnl': ['sum', 'count', 'mean']
    })
    sector_stats.columns = ['total_pnl', 'trade_count', 'avg_pnl']
    sector_stats = sector_stats.sort_values('total_pnl', ascending=False)

    output_dir = Path("docs/step4_3")
    data_dir = Path("data/results/step4_3")

    symbol_stats.to_csv(data_dir / "symbol_robustness.csv")
    sector_stats.to_csv(data_dir / "sector_robustness.csv")

    with open(output_dir / "SYMBOL_ROBUSTNESS.md", 'w') as f:
        f.write("# Step 4.3 Symbol Robustness\n\n## Concentration\n" + pd.DataFrame([concentration]).to_markdown() + "\n\n## Top 20 Contributors\n" + symbol_stats.head(20).to_markdown())

    with open(output_dir / "SECTOR_ROBUSTNESS.md", 'w') as f:
        f.write("# Step 4.3 Sector Robustness\n\n" + sector_stats.to_markdown())

if __name__ == "__main__":
    run_symbol_sector_audit()
