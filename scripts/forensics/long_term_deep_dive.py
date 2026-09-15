import sqlite3
import pandas as pd
import numpy as np
import json

db_path = "backend/local_operational.db"

def deep_dive():
    conn = sqlite3.connect(db_path)

    # 1. LONG_TERM Model Performance vs Features
    query = """
    SELECT symbol, roc_auc, brier_score, last_trained, accuracy
    FROM model_registry
    WHERE horizon = 'LONG' AND is_champion = 1
    """
    df = pd.read_sql_query(query, conn)

    print("=== LONG_TERM Model Forensics ===")
    print(df.describe().to_string())

    # Identify high AUC models
    high_auc = df[df['roc_auc'] > 0.85]
    print(f"\nModels with AUC > 0.85: {len(high_auc)} ({len(high_auc)/len(df)*100:.1f}%)")
    print(high_auc.head(10).to_string())

    # Identify failed models (AUC exactly 0.5)
    failed = df[df['roc_auc'] == 0.5]
    print(f"\nModels with AUC exactly 0.5: {len(failed)} ({len(failed)/len(df)*100:.1f}%)")

    # 2. Check Sample Sizes (by querying DuckDB indirectly or checking model metadata if stored)
    # The previous implementation didn't store training sample count in metadata.
    # Let's check a few symbols manually via SQL if possible or just infer from model failure.

    conn.close()

if __name__ == "__main__":
    deep_dive()
