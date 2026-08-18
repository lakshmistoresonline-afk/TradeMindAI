
import os
import sqlite3
import json

def audit():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    if not os.path.exists(db_path):
        print("DB not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, name, hyperparameters, calibration_metadata FROM model_registry WHERE is_champion = 1")
    rows = cursor.fetchall()

    audit_results = []

    for symbol, name, hyper_json, calib_json in rows:
        if "_" in symbol: continue

        try:
            hypers = json.loads(hyper_json) if hyper_json else {}
            calib = json.loads(calib_json) if calib_json else {}

            # Check feature count
            feature_names = hypers.get("feature_names", [])
            feature_count = len(feature_names)

            # Check max_depth and min_samples_leaf - wait, these are not in hypers usually unless saved there.
            # In MLService.train_and_register:
            # hyperparameters={"n_estimators": 100, "feature_names": feature_names}
            # It DOES NOT save max_depth or min_samples_leaf in hypers!

            audit_results.append({
                "symbol": symbol,
                "name": name,
                "feature_count": feature_count,
                "features": feature_names,
                "calibrated": "calibrator_file" in calib
            })
        except Exception as e:
            print(f"Error auditing {symbol}: {e}")

    print(f"Audited {len(audit_results)} pure champions.")

    incompatible = []
    for res in audit_results:
        if res['feature_count'] != 11:
            incompatible.append(res['symbol'])
            print(f"   [INCOMPATIBLE] {res['symbol']}: {res['feature_count']} features")
        else:
            # print(f"   [OK] {res['symbol']}: 11 features")
            pass

    print(f"Total Incompatible: {len(incompatible)}")

    # Save to JSON
    with open("production/audit/model_coverage.json", "w") as f:
        json.dump(audit_results, f, indent=4)

    conn.close()

if __name__ == "__main__":
    audit()
