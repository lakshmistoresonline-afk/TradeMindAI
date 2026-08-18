
import os
import sqlite3
import json

def promote():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Unmark all current champions for pure symbols
    cursor.execute("UPDATE model_registry SET is_champion = 0 WHERE symbol NOT LIKE '%\_%' ESCAPE '\\'")

    # 2. For every pure symbol, find the latest model with 11 features
    cursor.execute("SELECT name, symbol, hyperparameters FROM model_registry WHERE symbol NOT LIKE '%\_%' ESCAPE '\\' ORDER BY version DESC")
    rows = cursor.fetchall()

    promoted = 0
    symbols_covered = set()

    for name, symbol, hyper_json in rows:
        if symbol in symbols_covered: continue

        hypers = json.loads(hyper_json) if hyper_json else {}
        features = hypers.get("feature_names", [])

        if len(features) == 11:
            cursor.execute("UPDATE model_registry SET is_champion = 1 WHERE name = ?", (name,))
            symbols_covered.add(symbol)
            promoted += 1

    conn.commit()
    print(f"Force-promoted {promoted} v2.2 models to CHAMPION.")

    # Verify coverage again
    cursor.execute("SELECT count(*) FROM model_registry WHERE is_champion = 1 AND symbol NOT LIKE '%\_%' ESCAPE '\\'")
    count = cursor.fetchone()[0]
    print(f"Final CHAMPION count (pure symbols): {count}")

    conn.close()

if __name__ == "__main__":
    promote()
