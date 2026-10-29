"""
================================================================================
TradeMindAI: Pre-Reset Market Data Snapshot & SHA-256 Manifest Generator
================================================================================
Creates a complete, verifiable backup of all existing DuckDB tables, Parquet
feature stores, checkpoints, and derived signal history before Phase 0 reset.
Writes SHA256SUMS.txt manifest in backend/data/backup_snapshot_r4640/.
================================================================================
"""

import os
import shutil
import hashlib
import json
import duckdb
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
data_dir = root_dir / "backend" / "data"
backup_dir = data_dir / "backup_snapshot_r4640"
backup_dir.mkdir(parents=True, exist_ok=True)

backup_features_dir = backup_dir / "features"
backup_features_dir.mkdir(parents=True, exist_ok=True)

manifest = {}

def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def create_backup():
    print("=== [BACKUP] Starting Pre-Reset Snapshot Creation ===")

    # 1. Backup DuckDB
    duckdb_src = data_dir / "analytical.duckdb"
    if duckdb_src.exists():
        duckdb_dst = backup_dir / "analytical.duckdb"
        shutil.copy2(duckdb_src, duckdb_dst)
        sha = compute_sha256(duckdb_dst)
        manifest["analytical.duckdb"] = sha
        print(f"    [+] Backed up DuckDB: {sha[:16]}...")

    # 2. Backup Checkpoints & JSON assets
    json_files = ["ingestion_checkpoint.json", "sync_checkpoint.json", "shadow_sync_state.json", "signals_history.json", "ingestion_journal.json"]
    for j_file in json_files:
        src = data_dir / j_file
        if src.exists():
            dst = backup_dir / j_file
            shutil.copy2(src, dst)
            sha = compute_sha256(dst)
            manifest[j_file] = sha
            print(f"    [+] Backed up {j_file}: {sha[:16]}...")

    # 3. Backup Parquet Feature Stores
    features_src_dir = data_dir / "features"
    parquet_count = 0
    if features_src_dir.exists():
        for p_file in features_src_dir.glob("*.parquet"):
            dst = backup_features_dir / p_file.name
            shutil.copy2(p_file, dst)
            sha = compute_sha256(dst)
            manifest[f"features/{p_file.name}"] = sha
            parquet_count += 1
    print(f"    [+] Backed up {parquet_count} Parquet feature store files.")

    # 4. Save SHA256SUMS.txt
    sums_file = backup_dir / "SHA256SUMS.txt"
    with open(sums_file, "w", encoding="utf-8") as f:
        for name, sha in sorted(manifest.items()):
            f.write(f"{sha}  {name}\n")

    manifest_json = backup_dir / "manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"=== [BACKUP] Snapshot Completed Successfully ({len(manifest)} total files backed up) ===")

if __name__ == "__main__":
    create_backup()
