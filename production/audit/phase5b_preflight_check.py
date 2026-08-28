
import sqlite3
import json
import os
import hashlib

def calculate_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def preflight():
    db_path = "backend/local_operational.db"
    config_path = "production/strategy_v2_2/PRODUCTION_CONFIG.json"

    # 1. Config Hash
    config_hash = calculate_hash(config_path)
    print(f"Strategy v2.2 Config Hash: {config_hash}")

    # 2. Model Registry Audit
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Pure champions (no underscore in symbol)
    cursor.execute("SELECT symbol, name, hyperparameters FROM model_registry WHERE is_champion = 1 AND symbol NOT LIKE '%\_%' ESCAPE '\\'")
    pure_champions = cursor.fetchall()

    print(f"Total Pure Champions: {len(pure_champions)}")

    v2_2_compatible = 0
    feature_mismatch = []

    for symbol, name, hyper_json in pure_champions:
        hypers = json.loads(hyper_json) if hyper_json else {}
        features = hypers.get("feature_names", [])
        if len(features) == 11:
            v2_2_compatible += 1
        else:
            feature_mismatch.append(symbol)

    print(f"v2.2 Compatible (11 features): {v2_2_compatible}")
    print(f"Incompatible Pure Champions: {len(feature_mismatch)}")
    if feature_mismatch:
        print(f"Mismatched symbols: {feature_mismatch}")

    # 3. Check Exceptions
    exceptions = ["LTIM", "GUJGASLTD", "PEL", "TATAMOTORS"]
    print("\nException Audit:")
    for sym in exceptions:
        cursor.execute("SELECT count(*) FROM model_registry WHERE symbol = ?", (sym,))
        model_count = cursor.fetchone()[0]

        # Check historical data in PriceDB
        cursor.execute("SELECT count(*) FROM historical_prices WHERE symbol = ?", (sym,))
        price_count = cursor.fetchone()[0]

        print(f"  {sym}: Models={model_count}, Prices={price_count}")

    conn.close()

if __name__ == "__main__":
    preflight()
