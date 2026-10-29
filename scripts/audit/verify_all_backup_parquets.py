"""
================================================================================
TradeMindAI: Individual Parquet & Backup Inspection Script (Task 1)
================================================================================
Reads and validates every single Parquet file in backup_snapshot_r4640/features/
individually, recording row count, column count, and schema status for all 201 files.
Checks for unmanifested files in backup_snapshot_r4640/.
================================================================================
"""

import os
import hashlib
import duckdb
import pandas as pd
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
backup_dir = root_dir / "backend" / "data" / "backup_snapshot_r4640"
feat_backup_dir = backup_dir / "features"
sums_file = backup_dir / "SHA256SUMS.txt"

def verify_all_parquets():
    print("=== [TASK 1] Individual Parquet File Inspection ===")

    parquet_files = sorted(list(feat_backup_dir.glob("*.parquet")))
    print(f"[*] Total Parquet files found in backup: {len(parquet_files)}")

    valid_count = 0
    error_count = 0
    total_rows = 0

    parquet_manifest_records = []

    for idx, p_path in enumerate(parquet_files, 1):
        try:
            df = pd.read_parquet(p_path)
            row_cnt = len(df)
            col_cnt = len(df.columns)
            total_rows += row_cnt
            valid_count += 1
            parquet_manifest_records.append({
                "symbol": p_path.stem,
                "file_name": p_path.name,
                "row_count": row_cnt,
                "col_count": col_cnt,
                "status": "VALID"
            })
        except Exception as ex:
            error_count += 1
            print(f"[-] ERROR reading {p_path.name}: {ex}")
            parquet_manifest_records.append({
                "symbol": p_path.stem,
                "file_name": p_path.name,
                "row_count": 0,
                "col_count": 0,
                "status": f"ERROR: {ex}"
            })

    print(f"\n[+] Individual Parquet Verification Complete:")
    print(f"    - Inspected Files: {len(parquet_files)}")
    print(f"    - Valid Read Files: {valid_count}")
    print(f"    - Error Files: {error_count}")
    print(f"    - Cumulative Rows Across All Parquet Stores: {total_rows}")

    # Check for unmanifested files in backup_dir
    print("\n=== [TASK 1] Checking Unmanifested Files in Backup Directory ===")
    manifest_paths = set()
    if sums_file.exists():
        with open(sums_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("  ")
                if len(parts) == 2:
                    manifest_paths.add(parts[1])

    all_backed_up_files = []
    for root, _, files in os.walk(backup_dir):
        for file in files:
            full_p = Path(root) / file
            rel_p = full_p.relative_to(backup_dir).as_posix()
            all_backed_up_files.append(rel_p)

    unmanifested = [f for f in all_backed_up_files if f not in manifest_paths and f != "SHA256SUMS.txt" and f != "manifest.json"]
    print(f"[+] Total files in backup directory tree: {len(all_backed_up_files)}")
    print(f"[+] Manifest listed entries: {len(manifest_paths)}")
    print(f"[+] Unmanifested files count: {len(unmanifested)}")

if __name__ == "__main__":
    verify_all_parquets()
