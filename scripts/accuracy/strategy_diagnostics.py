
import os
import sys
import json
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def run_diagnostics():
    print("--- QUANTITATIVE STRATEGY DIAGNOSTICS ---")

    with engine.connect() as conn:
        # 1. Fetch all validation signals (IDs starting with val_ or wf_)
        query = text("""
            SELECT symbol, direction, conviction, calibrated_probability, expected_value,
                   status, profit_pct, regime, asset_class, data_quality_score, mfe, mae
            FROM live_signals
            WHERE id LIKE 'val_%' OR id LIKE 'wf_%'
        """)
        df = pd.read_sql(query, conn)

        if df.empty:
            print("[!] No validation signals found in database.")
            return

        print(f"Total Validation Signals: {len(df)}")

        # 2. Breakdown by Direction
        print("\n[Breakdown by Direction]")
        dir_stats = df.groupby('direction').agg({
            'status': lambda x: (x == 'TARGET_HIT').sum() / (x.isin(['TARGET_HIT', 'STOP_LOSS'])).sum() * 100,
            'profit_pct': 'mean',
            'symbol': 'count'
        }).rename(columns={'status': 'win_rate', 'symbol': 'count'})
        print(dir_stats)

        # 3. Breakdown by Regime
        print("\n[Breakdown by Regime]")
        if 'regime' in df.columns and df['regime'].notnull().any():
            regime_stats = df.groupby('regime').agg({
                'status': lambda x: (x == 'TARGET_HIT').sum() / (x.isin(['TARGET_HIT', 'STOP_LOSS'])).sum() * 100,
                'profit_pct': 'mean',
                'symbol': 'count'
            }).rename(columns={'status': 'win_rate', 'symbol': 'count'})
            print(regime_stats)
        else:
            print("Regime data unavailable.")

        # 4. Calibration Accuracy (Confidence Buckets)
        print("\n[Calibration Analysis]")
        df['prob_bucket'] = pd.cut(df['calibrated_probability'], bins=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        cal_stats = df.groupby('prob_bucket', observed=False).agg({
            'status': lambda x: (x == 'TARGET_HIT').sum() / (x.isin(['TARGET_HIT', 'STOP_LOSS'])).sum() if (x.isin(['TARGET_HIT', 'STOP_LOSS'])).any() else np.nan,
            'symbol': 'count'
        }).rename(columns={'status': 'observed_win_freq', 'symbol': 'count'})
        print(cal_stats)

        # 5. EV vs Reality
        print("\n[Expected Value Analysis]")
        df['ev_bucket'] = pd.qcut(df['expected_value'], q=4, duplicates='drop')
        ev_stats = df.groupby('ev_bucket', observed=False).agg({
            'profit_pct': 'mean',
            'status': lambda x: (x == 'TARGET_HIT').sum() / (x.isin(['TARGET_HIT', 'STOP_LOSS'])).sum() * 100 if (x.isin(['TARGET_HIT', 'STOP_LOSS'])).any() else 0,
            'symbol': 'count'
        }).rename(columns={'status': 'win_rate', 'symbol': 'count'})
        print(ev_stats)

        # 6. Sector Analysis
        print("\n[Sector Performance Audit]")
        # Need to join with stocks to get sector
        query_sector = text("""
            SELECT ls.symbol, s.sector, ls.status, ls.profit_pct
            FROM live_signals ls
            JOIN stocks s ON ls.symbol = s.symbol
            WHERE ls.id LIKE 'val_%'
        """)
        df_sector = pd.read_sql(query_sector, conn)
        if not df_sector.empty:
            sector_stats = df_sector.groupby('sector').agg({
                'status': lambda x: (x == 'TARGET_HIT').sum() / (x.isin(['TARGET_HIT', 'STOP_LOSS'])).sum() * 100 if (x.isin(['TARGET_HIT', 'STOP_LOSS'])).any() else 0,
                'profit_pct': 'mean',
                'symbol': 'count'
            }).rename(columns={'status': 'win_rate', 'symbol': 'count'})
            print(sector_stats.sort_values('win_rate', ascending=False))

        # 7. Dominant Failure Modes
        print("\n[Failure Mode Classification]")
        # For simulated signals, we look at mae/mfe to see if they were close or dead wrong
        query_failure = text("""
            SELECT direction, status, profit_pct, mfe, mae
            FROM live_signals
            WHERE id LIKE 'val_%' AND status = 'STOP_LOSS'
        """)
        df_fail = pd.read_sql(query_failure, conn)
        if not df_fail.empty:
            # Classification logic
            # False Breakout: MFE > 1% but still hit SL
            # Volatility Shock: MAE is very large negative
            # Trend Reversal: Profit was positive at some point but reversed
            df_fail['mode'] = 'UNKNOWN'
            df_fail.loc[df_fail['mfe'] > 1.5, 'mode'] = 'FALSE_BREAKOUT'
            df_fail.loc[df_fail['mae'] < -5.0, 'mode'] = 'VOLATILITY_SHOCK'
            df_fail.loc[(df_fail['mfe'] < 0.5) & (df_fail['mae'] > -2.0), 'mode'] = 'NO_MOMENTUM'

            print(df_fail['mode'].value_counts(normalize=True) * 100)

if __name__ == "__main__":
    run_diagnostics()
