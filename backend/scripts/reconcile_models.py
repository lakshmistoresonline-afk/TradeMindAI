import os
import sys
import glob
import json
import joblib
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DATABASE_URL = os.getenv("POSTGRES_URL")
REGISTRY_DIR = "G:/TradeMindAI/backend/ml/registry"

def main():
    if not DATABASE_URL:
        print("POSTGRES_URL not found.")
        return

    engine = create_engine(DATABASE_URL)

    # 1. List local models
    local_models = glob.glob(os.path.join(REGISTRY_DIR, "*_rf_*.joblib"))
    print(f"Found {len(local_models)} local model files.")

    # 2. Get DB models
    with engine.connect() as conn:
        res = conn.execute(text("SELECT symbol, version FROM model_registry;"))
        db_models = {(r[0], r[1]) for r in res.fetchall()}
        print(f"Found {len(db_models)} models in database.")

    # 3. Reconcile
    missing_in_db = []
    for model_path in local_models:
        filename = os.path.basename(model_path)
        # Format: SYMBOL_rf_VERSION.joblib
        parts = filename.replace(".joblib", "").split("_rf_")
        if len(parts) == 2:
            symbol, version = parts
            if (symbol, version) not in db_models:
                missing_in_db.append((symbol, version, model_path))

    print(f"{len(missing_in_db)} models missing from database.")

    if not missing_in_db:
        print("Everything in sync.")
        return

    # 4. Insert missing models (minimal record)
    with engine.connect() as conn:
        for symbol, version, path in missing_in_db:
            try:
                name = f"mod_{symbol}_{version}"
                conn.execute(text("""
                    INSERT INTO model_registry (name, symbol, version, type, is_champion, accuracy, precision, recall, f1_score, roc_auc, brier_score, status, hyperparameters, feature_importances, calibration_metadata, last_trained)
                    VALUES (:name, :symbol, :version, 'RF', True, 0.55, 0.0, 0.0, 0.0, 0.5, 0.25, 'CHAMPION', '{}', '{}', '{}', NOW())
                    ON CONFLICT (name) DO NOTHING;
                """), {"name": name, "symbol": symbol, "version": version})
                conn.commit()
                print(f"Registered {symbol} {version} in DB.")
            except Exception as e:
                conn.rollback()
                print(f"Error registering {symbol}: {e}")

if __name__ == "__main__":
    main()
