import sqlite3
import pandas as pd
import numpy as np

db_path = "backend/local_operational.db"

def run_forensic_audit():
    conn = sqlite3.connect(db_path)

    # 1. Model Registry Analysis
    print("=== MODEL REGISTRY SUMMARY ===")
    query = """
    SELECT horizon,
           COUNT(*) as model_count,
           AVG(roc_auc) as avg_auc,
           MIN(roc_auc) as min_auc,
           MAX(roc_auc) as max_auc,
           AVG(brier_score) as avg_brier
    FROM model_registry
    WHERE is_champion = 1
    GROUP BY horizon
    """
    df_models = pd.read_sql_query(query, conn)
    print(df_models.to_string())

    # 2. Signal Population Analysis
    print("\n=== SIGNAL POPULATION SUMMARY ===")
    query = """
    SELECT timeframe, direction, COUNT(*) as signal_count,
           AVG(calibrated_probability) as avg_prob,
           AVG(expected_value) as avg_ev
    FROM live_signals
    GROUP BY timeframe, direction
    """
    df_signals = pd.read_sql_query(query, conn)
    print(df_signals.to_string())

    # 3. High Performance Check (Verification of 0.85+ claims)
    print("\n=== MODELS WITH AUC > 0.80 ===")
    query = "SELECT horizon, symbol, roc_auc FROM model_registry WHERE roc_auc > 0.80 AND is_champion = 1"
    df_high = pd.read_sql_query(query, conn)
    print(f"Total models with AUC > 0.80: {len(df_high)}")
    print(df_high.groupby('horizon').count())

    # 4. Probability Bucket Check (Calibration Proxy)
    print("\n=== SIGNAL PROBABILITY BUCKETS ===")
    query = "SELECT calibrated_probability FROM live_signals"
    probs = pd.read_sql_query(query, conn)['calibrated_probability']
    bins = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 1.0]
    buckets = pd.cut(probs, bins)
    print(buckets.value_counts().sort_index())

    conn.close()

if __name__ == "__main__":
    run_forensic_audit()
