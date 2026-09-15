import os
import pandas as pd
import duckdb
import numpy as np

feature_storage = "backend/data/features"

def audit_samples():
    files = [f for f in os.listdir(feature_storage) if f.endswith(".parquet")]
    results = []

    print("=== Auditing LONG_TERM Training Samples ===")
    for f in files:
        symbol = f.replace(".parquet", "")
        file_path = os.path.join(feature_storage, f)
        df = pd.read_parquet(file_path)

        if 'target_long' not in df.columns:
            continue

        total = len(df)
        valid_long = df['target_long'].dropna()
        positives = (valid_long == 1).sum()
        negatives = (valid_long == 0).sum()

        results.append({
            'symbol': symbol,
            'total_rows': total,
            'labeled_rows': len(valid_long),
            'positives': positives,
            'negatives': negatives,
            'pos_ratio': positives / len(valid_long) if len(valid_long) > 0 else 0
        })

    df_res = pd.DataFrame(results)
    print(df_res.describe().to_string())

    print("\n=== Symbols with < 20 Positives for LONG ===")
    insufficient = df_res[df_res['positives'] < 20]
    print(f"Count: {len(insufficient)}")
    print(insufficient.head(20).to_string())

if __name__ == "__main__":
    audit_samples()
