
import os
import sqlite3

def check():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    model_dir = "backend/ml/registry"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, name, calibration_metadata FROM model_registry WHERE is_champion = 1")
    rows = cursor.fetchall()

    results = []
    for r in rows:
        symbol, model_name, calib_json = r
        if "_" in symbol: continue # Skip walk-forward/ablation

        model_path = os.path.join(model_dir, model_name)
        model_exists = os.path.exists(model_path)

        calib_exists = False
        import json
        try:
            calib_data = json.loads(calib_json) if calib_json else {}
            calib_file = calib_data.get("calibrator_file")
            if calib_file:
                calib_exists = os.path.exists(os.path.join(model_dir, calib_file))
        except: pass

        results.append({
            "symbol": symbol,
            "model_file": model_name,
            "model_exists": model_exists,
            "calib_exists": calib_exists
        })

    print(f"Total pure symbols checked: {len(results)}")
    missing_model = [r for r in results if not r['model_exists']]
    missing_calib = [r for r in results if not r['calib_exists']]

    print(f"Symbols missing model file: {len(missing_model)}")
    for m in missing_model: print(f"  {m['symbol']}: {m['model_file']}")

    print(f"Symbols missing calib file: {len(missing_calib)}")
    for m in missing_calib: print(f"  {m['symbol']}")

    valid_symbols = [r['symbol'] for r in results if r['model_exists']]
    print(f"Valid symbols (file exists): {len(valid_symbols)}")
    print(f"Valid Symbols: {', '.join(sorted(valid_symbols))}")

    conn.close()

if __name__ == "__main__":
    check()
