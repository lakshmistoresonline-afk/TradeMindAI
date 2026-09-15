import sqlite3
import pandas as pd

db_path = "backend/local_operational.db"

def verify_swing_auc():
    conn = sqlite3.connect(db_path)
    query = """
    SELECT symbol, roc_auc, brier_score, accuracy
    FROM model_registry
    WHERE horizon = 'SWING' AND is_champion = 1
    ORDER BY roc_auc DESC
    """
    df = pd.read_sql_query(query, conn)
    print("=== TOP 10 SWING MODELS BY AUC ===")
    print(df.head(10).to_string())

    print("\n=== AUC STATISTICS FOR SWING HORIZON ===")
    print(df['roc_auc'].describe().to_string())

    fail_count = len(df[df['roc_auc'] == 0.5])
    print(f"\nModels with AUC exactly 0.5: {fail_count} ({fail_count/len(df)*100:.1f}%)")

    conn.close()

if __name__ == "__main__":
    verify_swing_auc()
