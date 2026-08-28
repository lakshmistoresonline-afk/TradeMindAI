
import os
import sqlite3
import json

def find():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, hyperparameters, is_champion FROM model_registry")
    rows = cursor.fetchall()

    symbols_with_compatible_models = {}
    for symbol, hyper_json, is_champion in rows:
        if "_" in symbol: continue
        hypers = json.loads(hyper_json) if hyper_json else {}
        feature_names = hypers.get("feature_names", [])
        if len(feature_names) == 11:
            if symbol not in symbols_with_compatible_models:
                symbols_with_compatible_models[symbol] = []
            symbols_with_compatible_models[symbol].append(is_champion)

    print(f"Total symbols with AT LEAST ONE compatible model: {len(symbols_with_compatible_models)}")
    print(f"Symbols: {', '.join(sorted(symbols_with_compatible_models.keys()))}")

    for symbol, champions in symbols_with_compatible_models.items():
        if 1 not in champions:
            print(f"   [MISSING CHAMPION] {symbol} has compatible model but none marked as champion.")

    conn.close()

if __name__ == "__main__":
    find()
