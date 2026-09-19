import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

# Ensure Neon connection
os.environ["ENVIRONMENT"] = "production"
os.environ["SECRET_KEY"] = "A" * 32
os.environ["MARKET_DATA_INGEST_KEY"] = "SECURE_INGEST_KEY_2026"
os.environ["POSTGRES_URL"] = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

from backend.core.postgres import SessionLocal

def analyze():
    db = SessionLocal()
    try:
        shadow_cols = ["id", "status", "entry_price", "stop_price", "target_price", "calibrated_probability", "net_pnl"]
        live_cols = ["id", "status", "entry_price", "stop_price", "target_price", "calibrated_probability", "net_pnl"]

        query = text(f"""
            SELECT id, status, entry_price, stop_price, target_price, calibrated_probability, net_pnl FROM shadow_signals
            UNION ALL
            SELECT id, status, entry_price, stop_price, target_price, calibrated_probability, net_pnl FROM live_signals
        """)
        res = db.execute(query)
        df = pd.DataFrame([dict(row._mapping) for row in res.fetchall()])

        resolved = df[df['status'].isin(['TARGET_HIT', 'STOP_LOSS'])].copy()

        if resolved.empty:
            print("[!] No data.")
            return

        resolved['prob'] = pd.to_numeric(resolved['calibrated_probability'], errors='coerce')
        resolved['pnl'] = pd.to_numeric(resolved['net_pnl'], errors='coerce')

        # If PnL is missing, estimate it from entry/stop/target
        def estimate_pnl(row):
            if not pd.isna(row['pnl']): return row['pnl']
            if row['status'] == 'TARGET_HIT':
                return abs(row['target_price'] - row['entry_price']) / row['entry_price'] * 100
            else:
                return -abs(row['entry_price'] - row['stop_price']) / row['entry_price'] * 100

        resolved['est_pnl'] = resolved.apply(estimate_pnl, axis=1)

        print(f"[*] Baseline Population: N={len(resolved)}")
        print(f"    Win Rate: {(resolved['status'] == 'TARGET_HIT').mean() * 100:.2f}%")
        print(f"    Avg PnL: {resolved['est_pnl'].mean():.4f}%")

        thresholds = [0.55, 0.60, 0.65, 0.70]

        results = []
        for t in thresholds:
            filtered = resolved[resolved['prob'] >= t]

            if filtered.empty:
                results.append({"threshold": t, "count": 0, "win_rate": 0, "avg_pnl": 0, "signals_blocked": len(resolved)})
                continue

            results.append({
                "threshold": t,
                "count": len(filtered),
                "win_rate": round((filtered['status'] == 'TARGET_HIT').mean() * 100, 2),
                "avg_pnl": round(filtered['est_pnl'].mean(), 4),
                "signals_blocked": len(resolved) - len(filtered),
                "stop_loss_avoided": len(resolved[resolved['status'] == 'STOP_LOSS']) - len(filtered[filtered['status'] == 'STOP_LOSS']),
                "target_hit_lost": len(resolved[resolved['status'] == 'TARGET_HIT']) - len(filtered[filtered['status'] == 'TARGET_HIT'])
            })

        res_df = pd.DataFrame(results)
        print("\nNO-SIGNAL ANALYSIS (Impact of Probability Gating):")
        print(res_df.to_markdown(index=False))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze()
