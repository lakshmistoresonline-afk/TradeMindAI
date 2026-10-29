"""
================================================================================
TradeMindAI: Controlled Market Data Reset Script (Phase 0)
================================================================================
Executes controlled reset of Category A (stale market data) and Category B
(obsolete ingestion artifacts) AFTER verifying backup snapshot.
Preserves DuckDB schema/tables, frontend assets, configuration, and security settings.
================================================================================
"""

import os
import json
import duckdb
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
data_dir = root_dir / "backend" / "data"
backup_dir = data_dir / "backup_snapshot_r4640"
features_dir = data_dir / "features"
duckdb_path = data_dir / "analytical.duckdb"

def verify_backup_before_reset():
    if not backup_dir.exists() or not (backup_dir / "SHA256SUMS.txt").exists():
        raise RuntimeError("CRITICAL SAFETY BLOCK: Backup snapshot missing or incomplete. Refusing reset!")
    print("[+] Verified backup snapshot exists at:", backup_dir)

def execute_reset():
    verify_backup_before_reset()
    print("=== [RESET] Executing Controlled Market Data Reset ===")

    # 1. Reset DuckDB daily_ohlcv table (preserving table schema, columns, constraints)
    if duckdb_path.exists():
        con = duckdb.connect(str(duckdb_path))
        pre_count = con.execute("SELECT count(*) FROM daily_ohlcv").fetchone()[0]
        con.execute("DELETE FROM daily_ohlcv;")
        post_count = con.execute("SELECT count(*) FROM daily_ohlcv").fetchone()[0]
        con.close()
        print(f"    [+] DuckDB 'daily_ohlcv' reset: {pre_count} -> {post_count} rows.")

    # 2. Reset Parquet Feature Store Files in Category A
    removed_parquet = 0
    if features_dir.exists():
        for p_file in features_dir.glob("*.parquet"):
            p_file.unlink()
            removed_parquet += 1
    print(f"    [+] Parquet Feature Store reset: {removed_parquet} files removed.")

    # 3. Reset Ingestion Checkpoints in Category B
    checkpoint_file = data_dir / "ingestion_checkpoint.json"
    if checkpoint_file.exists():
        checkpoint_file.write_text("{}\n", encoding="utf-8")
        print("    [+] Reset ingestion_checkpoint.json -> {}")

    sync_checkpoint_file = data_dir / "sync_checkpoint.json"
    if sync_checkpoint_file.exists():
        sync_checkpoint_file.write_text("{}\n", encoding="utf-8")
        print("    [+] Reset sync_checkpoint.json -> {}")

    journal_file = data_dir / "ingestion_journal.json"
    if journal_file.exists():
        journal_file.unlink()
        print("    [+] Removed obsolete ingestion_journal.json")

    print("=== [RESET] Market Data Reset Complete ===")

if __name__ == "__main__":
    execute_reset()
