
import os
import sqlite3
import json
from datetime import datetime

def generate():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, name, version, hyperparameters, calibration_metadata, last_trained FROM model_registry WHERE is_champion = 1")
    rows = cursor.fetchall()

    manifest = []
    for r in rows:
        symbol, name, version, hyper_json, calib_json, created_at = r
        if "_" in symbol: continue

        hypers = json.loads(hyper_json) if hyper_json else {}
        calib = json.loads(calib_json) if calib_json else {}

        manifest.append({
            "symbol": symbol,
            "model_version": version,
            "strategy_version": "v2.2",
            "model_type": "RANDOM_FOREST",
            "feature_count": len(hypers.get("feature_names", [])),
            "file_path": f"backend/ml/registry/{name}",
            "created_at": created_at,
            "status": "ACTIVE"
        })

    os.makedirs("production/models", exist_ok=True)
    with open("production/models/MODEL_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Generated manifest for {len(manifest)} models.")
    conn.close()

if __name__ == "__main__":
    generate()
