
import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def deep_dive():
    print("--- FAILURE MODE DEEP DIVE ---")

    with engine.connect() as conn:
        query = text("""
            SELECT symbol, direction, mfe, mae, profit_pct, entry_price, target_price, stop_loss_price
            FROM live_signals
            WHERE id LIKE 'val_%' OR id LIKE 'wf_%'
            AND status = 'STOP_LOSS'
        """)
        df = pd.read_sql(query, conn)

        if df.empty:
            print("[!] No losing signals found for deep dive.")
            return

        print(f"Analyzing {len(df)} losing signals...")

        # Classification
        # 1. Trend Reversal: Made progress towards target, then reversed.
        #    Target is usually ~5% away. If MFE > 1.5%, it's a significant move.
        df['mode'] = 'UNKNOWN'
        df.loc[df['mfe'] >= 1.5, 'mode'] = 'TREND_REVERSAL'
        df.loc[df['mfe'] < 1.0, 'mode'] = 'FALSE_BREAKOUT'
        df.loc[(df['mfe'] >= 1.0) & (df['mfe'] < 1.5), 'mode'] = 'STALL_AND_REVERSE'

        stats = df['mode'].value_counts(normalize=True) * 100
        print("\n[Failure Mode Distribution]")
        print(stats)

        # 2. Distance from Entry to Stop
        # If MAE is very small, it means the stop was hit immediately.
        # If MAE is large, it was a slow bleed or volatility shock.
        df['risk_distance'] = (df['entry_price'] - df['stop_loss_price']).abs() / df['entry_price'] * 100
        print(f"\nAvg Risk distance (Stop): {df['risk_distance'].mean():.2f}%")

        # 3. Volatility Shock Check
        # If mae << stop_loss_price (in direction), it means price gapped or spiked.
        # OutcomeEngine assumes Stop Hit at stop_price.
        # But MAE tells us how far it *really* went against us.

        df_reversal = df[df['mode'] == 'TREND_REVERSAL']
        print(f"\n[Trend Reversal Insights]")
        print(f"Avg MFE before reversal: {df_reversal['mfe'].mean():.2f}%")

if __name__ == "__main__":
    deep_dive()
