
import os
import sqlite3
import json

def verify():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, name, hyperparameters FROM model_registry WHERE is_champion = 1")
    rows = cursor.fetchall()

    compatible = []
    incompatible = []

    for symbol, name, hyper_json in rows:
        if "_" in symbol: continue
        hypers = json.loads(hyper_json) if hyper_json else {}
        features = hypers.get("feature_names", [])
        if len(features) == 11:
            compatible.append(symbol)
        else:
            incompatible.append(symbol)

    print(f"Total symbols with champions: {len(compatible) + len(incompatible)}")
    print(f"V2.2 Compatible (11 features): {len(compatible)}")
    print(f"V2.1 Incompatible (legacy): {len(incompatible)}")

    if incompatible:
        print(f"Incompatible Symbols: {', '.join(sorted(incompatible))}")

    conn.close()

if __name__ == "__main__":
    verify()
