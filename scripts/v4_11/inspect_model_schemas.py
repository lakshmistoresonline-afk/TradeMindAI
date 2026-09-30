import os
import sys
import json
import hashlib
from pathlib import Path
import joblib

ROOT_DIR = Path("G:/TradeMindAI")
sys.path.append(str(ROOT_DIR))

RAW_DIR = ROOT_DIR / "docs" / "V4_11" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_DIR = ROOT_DIR / "backend" / "ml" / "registry"

symbols = ["RELIANCE", "TCS", "HDFCBANK"]

def sha256_sum(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def inspect_schemas():
    print("==========================================================================")
    print(" TradeMind AI V4.11: Model Schema Inspection")
    print("==========================================================================")

    joblib_files = list(REGISTRY_DIR.glob("*.joblib"))

    for sym in symbols:
        print(f"\n[Inspect] Symbol: {sym}")
        match_files = [f for f in joblib_files if sym in f.name and "model" in f.name]
        if not match_files:
            print(f"[Warning] No model found for {sym}")
            continue

        model_path = match_files[0]
        file_sha = sha256_sum(model_path)

        schema_record = {
            "symbol": sym,
            "artifact_path": str(model_path.relative_to(ROOT_DIR)),
            "filename": model_path.name,
            "sha256": file_sha
        }

        try:
            model = joblib.load(model_path)
            schema_record["model_class"] = str(type(model))

            if hasattr(model, "n_features_in_"):
                schema_record["n_features_in_"] = int(model.n_features_in_)
            else:
                schema_record["n_features_in_"] = None

            if hasattr(model, "feature_names_in_"):
                schema_record["feature_names_in_"] = list(model.feature_names_in_)
            else:
                schema_record["feature_names_in_"] = None

            if hasattr(model, "classes_"):
                schema_record["classes_"] = model.classes_.tolist()
            else:
                schema_record["classes_"] = None

            schema_record["load_status"] = "SUCCESS"
            print(f"[+] {model_path.name}: n_features_in_ = {schema_record['n_features_in_']}, feature_names_in_ = {len(schema_record['feature_names_in_']) if schema_record['feature_names_in_'] is not None else 'None'}")

        except Exception as e:
            schema_record["load_status"] = "FAILED"
            schema_record["error"] = str(e)
            print(f"[!] Failed to inspect {model_path.name}: {e}")

        with open(RAW_DIR / f"model_schema_{sym}.json", "w", encoding="utf-8") as f:
            json.dump(schema_record, f, indent=2)

    print("\n[+] Model Schema Inspection Complete.")

if __name__ == "__main__":
    inspect_schemas()
