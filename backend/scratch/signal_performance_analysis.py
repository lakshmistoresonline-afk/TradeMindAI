import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

# Load environment
os.environ["ENVIRONMENT"] = "production"
os.environ["SECRET_KEY"] = "A" * 32
os.environ["MARKET_DATA_INGEST_KEY"] = "SECURE_INGEST_KEY_2026"
os.environ["POSTGRES_URL"] = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

from backend.core.postgres import SessionLocal

def analyze():
    db = SessionLocal()
    try:
        # Extract all signals
        cols = ["id", "symbol", "direction", "status", "entry_price", "stop_price", "target_price", "conviction", "calibrated_probability", "regime", "timeframe", "realized_mfe", "realized_mae"]
        col_str = ", ".join(cols)

        query = text(f"""
            SELECT {col_str} FROM shadow_signals
            UNION ALL
            SELECT {col_str} FROM live_signals
        """)
        res = db.execute(query)
        all_signals = [dict(zip(cols, row)) for row in res.fetchall()]

        df = pd.DataFrame(all_signals)
        # Resolved only for performance metrics
        resolved = df[df['status'].in_(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'])].copy()

        # 1. STOP DISTANCE ANALYSIS
        resolved['stop_dist_pct'] = (abs(resolved['entry_price'] - resolved['stop_price']) / resolved['entry_price'] * 100)

        print("[*] Stop Distance Analysis...")
        # Bin stop distances
        resolved['stop_bin'] = pd.cut(resolved['stop_dist_pct'], bins=[0, 1, 2, 3, 5, 10, 100])
        stop_perf = resolved.groupby('stop_bin', observed=False).agg(
            count=('id', 'count'),
            win_rate=('status', lambda x: (x == 'TARGET_HIT').mean() * 100),
            avg_mfe=('realized_mfe', 'mean')
        )
        print(stop_perf)

        # 2. SIGNAL SCORE ANALYSIS
        print("\n[*] Conviction Score Analysis...")
        resolved['score_bin'] = pd.cut(resolved['conviction'], bins=[0, 50, 60, 70, 80, 90, 100])
        score_perf = resolved.groupby('score_bin', observed=False).agg(
            count=('id', 'count'),
            win_rate=('status', lambda x: (x == 'TARGET_HIT').mean() * 100)
        )
        print(score_perf)

        # 3. PROBABILITY CALIBRATION
        print("\n[*] Probability Calibration...")
        resolved['prob_bin'] = pd.cut(resolved['calibrated_probability'], bins=[0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        prob_perf = resolved.groupby('prob_bin', observed=False).agg(
            count=('id', 'count'),
            avg_pred_prob=('calibrated_probability', 'mean'),
            actual_win_rate=('status', lambda x: (x == 'TARGET_HIT').mean())
        )
        prob_perf['error'] = prob_perf['actual_win_rate'] - prob_perf['avg_pred_prob']
        print(prob_perf)

        # 4. REGIME PERFORMANCE
        print("\n[*] Regime Performance...")
        regime_perf = resolved.groupby('regime', observed=False).agg(
            count=('id', 'count'),
            win_rate=('status', lambda x: (x == 'TARGET_HIT').mean() * 100)
        )
        print(regime_perf)

        # Save analysis reports
        os.makedirs("reports", exist_ok=True)

        with open("reports/SIGNAL_CALIBRATION_ANALYSIS.md", "w") as f:
            f.write("# Signal Calibration Analysis\n\n")
            f.write("## Probability Calibration\n")
            f.write(prob_perf.to_markdown())
            f.write("\n\n## Conviction Score vs Win Rate\n")
            f.write(score_perf.to_markdown())

        with open("reports/STOP_TARGET_ANALYSIS.md", "w") as f:
            f.write("# Stop and Target Analysis\n\n")
            f.write("## Stop Distance vs Performance\n")
            f.write(stop_perf.to_markdown())

        with open("reports/REGIME_FAILURE_ANALYSIS.md", "w") as f:
            f.write("# Regime Failure Analysis\n\n")
            f.write(regime_perf.to_markdown())

        print("\n[SUCCESS] Performance reports saved.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze()
