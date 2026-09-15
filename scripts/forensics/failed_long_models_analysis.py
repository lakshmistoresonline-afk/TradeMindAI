import sqlite3
import pandas as pd
import os

db_path = "backend/local_operational.db"
feature_storage = "backend/data/features"

def analyze_failed_models():
    conn = sqlite3.connect(db_path)
    query = "SELECT symbol FROM model_registry WHERE horizon = 'LONG' AND roc_auc = 0.5 AND is_champion = 1"
    failed_symbols = pd.read_sql_query(query, conn)['symbol'].tolist()

    print(f"Total failed LONG models: {len(failed_symbols)}")

    results = []
    for symbol in failed_symbols[:20]:
        file_path = os.path.join(feature_storage, f"{symbol}.parquet")
        if not os.path.exists(file_path): continue

        df = pd.read_parquet(file_path)
        y = df['target_long'].dropna()

        # Simulate 70/15/15 split
        n = len(y)
        test_start = int(n * 0.85)
        y_test = y.iloc[test_start:]

        results.append({
            'symbol': symbol,
            'test_positives': (y_test == 1).sum(),
            'test_negatives': (y_test == 0).sum(),
            'test_size': len(y_test)
        })

    df_res = pd.DataFrame(results)
    print("\n=== Test Set Distribution for Failed Models ===")
    print(df_res.to_string())

    conn.close()

if __name__ == "__main__":
    analyze_failed_models()
