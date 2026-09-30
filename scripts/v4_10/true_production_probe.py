import os
import sys
import json
import hashlib
from pathlib import Path
import joblib
import numpy as np

ROOT_DIR = Path("G:/TradeMindAI")
sys.path.append(str(ROOT_DIR))

RAW_DIR = ROOT_DIR / "docs" / "V4_10" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_DIR = ROOT_DIR / "backend" / "ml" / "registry"

symbols = ["RELIANCE", "TCS", "HDFCBANK"]

def sha256_sum(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def probe_production_models():
    print("==========================================================================")
    print(" TradeMind AI V4.10: True Production Model Execution Probe (40 Features)")
    print("==========================================================================")

    joblib_files = list(REGISTRY_DIR.glob("*.joblib"))

    for sym in symbols:
        print(f"\n[Probe] Probing Symbol: {sym}")

        match_files = [f for f in joblib_files if sym in f.name and "model" in f.name]
        if not match_files:
            continue

        model_path = match_files[0]
        model_name = model_path.name
        file_size = model_path.stat().st_size
        file_sha = sha256_sum(model_path)

        load_record = {
            "symbol": sym,
            "artifact_path": str(model_path.relative_to(ROOT_DIR)),
            "filename": model_name,
            "size_bytes": file_size,
            "sha256": file_sha,
            "load_success": True
        }

        try:
            model = joblib.load(model_path)
            load_record["model_class"] = str(type(model))

            # ExtraTreesClassifier expects 40 features
            dummy_features = np.zeros((1, 40))

            inference_record = {
                "symbol": sym,
                "filename": model_name,
                "input_shape": [1, 40]
            }

            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(dummy_features)
                inference_record["predict_proba_output"] = proba.tolist()
                inference_record["inference_success"] = True
                print(f"[+] predict_proba executed successfully: {proba}")
            elif hasattr(model, "predict"):
                pred = model.predict(dummy_features)
                inference_record["predict_output"] = pred.tolist()
                inference_record["inference_success"] = True
                print(f"[+] predict executed successfully: {pred}")

        except Exception as e:
            load_record["load_success"] = False
            load_record["error"] = str(e)
            inference_record = {"symbol": sym, "error": str(e), "inference_success": False}

        with open(RAW_DIR / f"model_load_{sym}.json", "w", encoding="utf-8") as f:
            json.dump(load_record, f, indent=2)

        with open(RAW_DIR / f"model_inference_{sym}.json", "w", encoding="utf-8") as f:
            json.dump(inference_record, f, indent=2)

    print("\n[+] V4.10 True Production Probe Complete with 40-feature vector.")

if __name__ == "__main__":
    probe_production_models()
