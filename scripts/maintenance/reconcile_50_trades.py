import os
import sys
import pandas as pd
import json
from datetime import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine
from backend.services.pnl_engine import PNLEngine
from backend.services.drawdown_service import DrawdownService

def run_reconciliation():
    print("--- TRADEMIND AI: 50-TRADE MASTER RECONCILIATION ---")

    with engine.connect() as conn:
        # 1. Fetch Authoritative Data
        query = text("""
            SELECT id, symbol, direction, entry_price, exit_price, status, net_pnl, pnl_percentage
            FROM shadow_signals
            WHERE outcome_verified = TRUE
            ORDER BY outcome_timestamp ASC
        """)
        trades = conn.execute(query).fetchall()
        df = pd.DataFrame(trades)

        print(f"Total Verified Trades in SQL: {len(df)}")

        # 2. Recalculate P&L using PNLEngine
        mismatches = []
        for idx, row in df.iterrows():
            calc = PNLEngine.calculate_pnl(row['entry_price'], row['exit_price'], row['direction'])
            # Compare with existing net_pnl (stored as pct)
            if abs(calc['net_pnl_pct'] - row['net_pnl']) > 0.01:
                mismatches.append({
                    "id": row['id'], "sym": row['symbol'],
                    "stored": row['net_pnl'], "calc": calc['net_pnl_pct']
                })

        print(f"P&L Mismatches detected: {len(mismatches)}")
        for m in mismatches:
            print(f"  [!] {m['sym']} ({m['id']}): Stored={m['stored']}% vs Calc={m['calc']}%")

        # 3. Recalculate Drawdowns
        returns = df['net_pnl'].tolist()
        trade_dd = DrawdownService.calculate_trade_sequence_drawdown(returns)
        print(f"\nRecalculated Trade Sequence Max Drawdown: {trade_dd:.2f}%")

        # 4. Global Performance
        wins = len(df[df['status'] == 'TARGET_HIT'])
        wr = (wins / len(df)) * 100
        print(f"Verified Win Rate: {wr:.2f}%")
        print(f"Total Net P&L:     {df['net_pnl'].sum():.2f}%")

if __name__ == "__main__":
    run_reconciliation()
