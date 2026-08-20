import pandas as pd
import numpy as np
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def run_symbol_sector_audit():
    trades_path = 'data/results/portfolio_trades.csv'
    if not os.path.exists(trades_path):
        print("Ledger missing.")
        return

    df = pd.read_csv(trades_path)

    # 1. Symbol Robustness
    symbol_stats = df.groupby('symbol').agg({
        'net_pnl': ['sum', 'count', 'mean'],
        'pnl': lambda x: (x > 0).mean() * 100
    }).reset_index()

    symbol_stats.columns = ['symbol', 'total_pnl', 'trade_count', 'avg_pnl', 'win_rate']
    symbol_stats = symbol_stats.sort_values('total_pnl', ascending=False)

    top_20 = symbol_stats.head(20)
    bottom_20 = symbol_stats.tail(20)

    total_net = df['net_pnl'].sum()
    pnl_no_top1 = total_net - top_20.iloc[0]['total_pnl']
    pnl_no_top5 = total_net - top_20.head(5)['total_pnl'].sum()
    pnl_no_top10 = total_net - top_20.head(10)['total_pnl'].sum()

    # 2. Sector Robustness
    conn = sqlite3.connect('backend/local_operational.db')
    sector_map = pd.read_sql_query("SELECT symbol, sector FROM stocks", conn).set_index('symbol')['sector'].to_dict()
    conn.close()

    df['sector'] = df['symbol'].map(sector_map).fillna('Unknown')

    sector_stats = df.groupby('sector').agg({
        'net_pnl': ['sum', 'count', 'mean'],
        'pnl': lambda x: (x > 0).mean() * 100
    }).reset_index()
    sector_stats.columns = ['sector', 'total_pnl', 'trade_count', 'avg_pnl', 'win_rate']
    sector_stats = sector_stats.sort_values('total_pnl', ascending=False)

    # Concentration
    top1_pct = (top_20.iloc[0]['total_pnl'] / total_net) * 100
    top5_pct = (top_20.head(5)['total_pnl'].sum() / total_net) * 100

    report_md = f"""# TradeMind AI - Step 4.3 Symbol & Sector Robustness

## Concentration Risk
- **Top 1 Symbol Contribution**: {top1_pct:.2f}% ({top_20.iloc[0]['symbol']})
- **Top 5 Symbols Contribution**: {top5_pct:.2f}%
- **Total Net PnL (Base)**: {total_net:,.2f}
- **PnL without Top 1**: {pnl_no_top1:,.2f}
- **PnL without Top 10**: {pnl_no_top10:,.2f}

## Sector Breakdown
{sector_stats.to_markdown(index=False)}

## Top 10 Symbols
{symbol_stats.head(10).to_markdown(index=False)}

## Bottom 10 Symbols
{symbol_stats.tail(10).to_markdown(index=False)}
"""
    with open('docs/step4_3/SYMBOL_ROBUSTNESS.md', 'w') as f:
        f.write(report_md)

    symbol_stats.to_csv('data/results/step4_3/symbol_robustness.csv', index=False)
    sector_stats.to_csv('data/results/step4_3/sector_robustness.csv', index=False)
    print("Generated docs/step4_3/SYMBOL_ROBUSTNESS.md")

if __name__ == "__main__":
    run_symbol_sector_audit()
