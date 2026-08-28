
import os
import sqlite3
import json

def find():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, hyperparameters FROM model_registry WHERE is_champion = 1")
    rows = cursor.fetchall()

    compatible = []
    for symbol, hyper_json in rows:
        if "_" in symbol: continue
        hypers = json.loads(hyper_json) if hyper_json else {}
        feature_names = hypers.get("feature_names", [])
        if len(feature_names) == 11:
            compatible.append(symbol)

    print(f"Compatible symbols (11 features): {len(compatible)}")
    print(f"Symbols: {', '.join(sorted(compatible))}")
    conn.close()

if __name__ == "__main__":
    find()
