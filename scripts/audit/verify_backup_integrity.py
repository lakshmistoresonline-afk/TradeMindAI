"""
================================================================================
TradeMindAI: Forensic Backup Verification Script (Task 1)
================================================================================
Recomputes SHA-256 digests for all files listed in SHA256SUMS.txt in
backend/data/backup_snapshot_r4640/, verifies DuckDB database readability,
and inspects Parquet schemas read-only.
================================================================================
"""

import hashlib
import duckdb
import pandas as pd
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
backup_dir = root_dir / "backend" / "data" / "backup_snapshot_r4640"
sums_file = backup_dir / "SHA256SUMS.txt"

def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_backup_integrity():
    print("=== [TASK 1] Forensic Backup Hash Verification ===")
    if not sums_file.exists():
        print("[-] FAIL: SHA256SUMS.txt missing in backup directory!")
        return

    expected_hashes = {}
    with open(sums_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("  ")
            if len(parts) == 2:
                sha, rel_path = parts
                expected_hashes[rel_path] = sha

    print(f"[*] Manifest contains {len(expected_hashes)} expected file entries.")

    matches = 0
    mismatches = 0
    missing = 0

    for rel_path, expected_sha in expected_hashes.items():
        file_path = backup_dir / rel_path
        if not file_path.exists():
            print(f"[-] MISSING: {rel_path}")
            missing += 1
            continue

        recomputed_sha = compute_sha256(file_path)
        if recomputed_sha == expected_sha:
            matches += 1
        else:
            print(f"[-] MISMATCH: {rel_path} (expected {expected_sha[:12]}, got {recomputed_sha[:12]})")
            mismatches += 1

    print(f"\n[+] Hash Verification Summary: Matches={matches}, Mismatches={mismatches}, Missing={missing}")

    # Verify Backed-Up DuckDB Readability
    print("\n=== [TASK 1] Verifying Backed-Up DuckDB Database ===")
    db_backup = backup_dir / "analytical.duckdb"
    if db_backup.exists():
        try:
            con = duckdb.connect(str(db_backup), read_only=True)
            tables = con.execute("SHOW TABLES").fetchall()
            print(f"[+] Backed-up DuckDB contains {len(tables)} tables: {[t[0] for t in tables]}")
            for t in tables:
                t_name = t[0]
                cnt = con.execute(f"SELECT count(*) FROM {t_name}").fetchone()[0]
                print(f"    - Table '{t_name}': {cnt} rows")
            con.close()
        except Exception as ex:
            print(f"[-] DuckDB Backup Read Error: {ex}")
    else:
        print("[-] DuckDB backup file missing.")

    # Verify Backed-Up Parquet Store Readability
    print("\n=== [TASK 1] Verifying Backed-Up Parquet Feature Stores ===")
    feat_backup_dir = backup_dir / "features"
    parquet_files = list(feat_backup_dir.glob("*.parquet"))
    print(f"[+] Found {len(parquet_files)} Parquet files in backup directory.")
    if parquet_files:
        sample_p = parquet_files[0]
        try:
            df = pd.read_parquet(sample_p)
            print(f"[+] Sample Parquet ({sample_p.name}) readable: {len(df)} rows, columns: {list(df.columns)}")
        except Exception as ex:
            print(f"[-] Parquet Read Error: {ex}")

if __name__ == "__main__":
    verify_backup_integrity()
