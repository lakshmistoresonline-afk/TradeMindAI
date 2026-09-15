import sqlite3
import json
import pandas as pd

db_path = "backend/local_operational.db"

def analyze_calibration():
    conn = sqlite3.connect(db_path)
    query = """
    SELECT horizon, calibration_metadata
    FROM model_registry
    WHERE is_champion = 1
    """
    df = pd.read_sql_query(query, conn)

    results = []
    for _, row in df.iterrows():
        try:
            meta = json.loads(row['calibration_metadata'])
            results.append({
                'horizon': row['horizon'],
                'brier_calib': meta.get('brier_score_calibrated'),
                'logloss_calib': meta.get('log_loss_calibrated')
            })
        except:
            continue

    df_res = pd.DataFrame(results)
    print("=== CALIBRATION METRICS BY HORIZON ===")
    print(df_res.groupby('horizon').mean().to_string())

    conn.close()

if __name__ == "__main__":
    analyze_calibration()
