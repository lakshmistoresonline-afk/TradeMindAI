import os
import glob
import hashlib
import json
from pathlib import Path

REGISTRY_DIR = Path("G:/TradeMindAI/backend/ml/registry")

def sha256_sum(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def audit_models():
    if not REGISTRY_DIR.exists():
        print(f"Registry dir not found: {REGISTRY_DIR}")
        return

    joblib_files = list(REGISTRY_DIR.glob("*.joblib"))
    total_files = len(joblib_files)

    model_artifacts = []
    calibrators = []
    rf_artifacts = []
    platt_artifacts = []
    others = []
    unrecognized = []

    content_hashes = {}
    duplicate_content = 0
    symbol_horizon_map = {}
    duplicate_symbol_horizon = 0

    for f in joblib_files:
        name = f.name
        size = f.stat().st_size
        mtime = f.stat().st_mtime
        c_hash = sha256_sum(f)

        if c_hash in content_hashes:
            duplicate_content += 1
        else:
            content_hashes[c_hash] = name

        item = {
            "filename": name,
            "size_bytes": size,
            "sha256": c_hash,
            "mtime": mtime
        }

        if "calib" in name.lower():
            calibrators.append(item)
        elif "platt" in name.lower():
            platt_artifacts.append(item)
        elif "_rf_" in name.lower():
            rf_artifacts.append(item)
        elif any(k in name.upper() for k in ["_SWING_", "_LONG_", "_SHORT_"]):
            model_artifacts.append(item)
            # Check symbol + horizon
            parts = name.split("_")
            if len(parts) >= 2:
                sym_hor = f"{parts[0]}_{parts[1]}"
                if sym_hor in symbol_horizon_map:
                    duplicate_symbol_horizon += 1
                else:
                    symbol_horizon_map[sym_hor] = name
        else:
            others.append(item)

    report = {
        "total_joblib_files": total_files,
        "model_artifact_files": len(model_artifacts),
        "calibrator_artifact_files": len(calibrators),
        "rf_artifact_files": len(rf_artifacts),
        "platt_artifact_files": len(platt_artifacts),
        "other_artifact_files": len(others),
        "unrecognized_artifact_files": len(unrecognized),
        "duplicate_content_files": duplicate_content,
        "duplicate_symbol_horizon_files": duplicate_symbol_horizon,
        "unique_model_identities": len(symbol_horizon_map)
    }

    out_path = Path("G:/TradeMindAI/docs/forensics/model_registry_audit.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(report, out, indent=2)

    print("Model Registry Audit Complete:", report)

if __name__ == "__main__":
    audit_models()
