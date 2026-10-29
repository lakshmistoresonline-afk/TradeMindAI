"""
================================================================================
TradeMindAI: Live Database & Data Artifact Read-Only Audit (Tasks 2 & 3)
================================================================================
Inspects live analytical DuckDB database, features directory, checkpoints,
and data artifacts read-only.
================================================================================
"""

import os
import json
import duckdb
import pandas as pd
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
data_dir = root_dir / "backend" / "data"

def inspect_live_databases():
    print("=== [TASK 2 & 3] Live Database and Artifact Inspection ===")

    # 1. Inspect Live DuckDB
    duckdb_live = data_dir / "analytical.duckdb"
    print(f"\n[*] Live DuckDB File: {duckdb_live} (Size: {duckdb_live.stat().st_size if duckdb_live.exists() else 0} bytes)")
    if duckdb_live.exists():
        try:
            con = duckdb.connect(str(duckdb_live), read_only=True)
            tables = con.execute("SHOW TABLES").fetchall()
            print(f"[+] Live DuckDB Tables: {[t[0] for t in tables]}")
            for t in tables:
                t_name = t[0]
                cnt = con.execute(f"SELECT count(*) FROM {t_name}").fetchone()[0]
                schema = con.execute(f"DESCRIBE {t_name}").fetchall()
                cols = [s[0] for s in schema]
                print(f"    - Table '{t_name}': {cnt} rows, Columns: {cols}")
            con.close()
        except Exception as ex:
            print(f"[-] Live DuckDB Read Error: {ex}")

    # 2. Inspect Live Parquet Feature Store
    feat_live_dir = data_dir / "features"
    parquet_live_files = list(feat_live_dir.glob("*.parquet")) if feat_live_dir.exists() else []
    print(f"\n[*] Live Parquet Feature Store: {len(parquet_live_files)} .parquet files in {feat_live_dir}")

    # 3. Inspect Forensics Directory
    forensics_dir = data_dir / "forensics"
    forensics_files = list(forensics_dir.glob("*")) if forensics_dir.exists() else []
    print(f"[*] Live Forensics Directory: {len(forensics_files)} files in {forensics_dir}")

    # 4. Inspect Checkpoints and JSON Assets
    json_targets = {
        "ingestion_checkpoint.json": data_dir / "ingestion_checkpoint.json",
        "sync_checkpoint.json": data_dir / "sync_checkpoint.json",
        "shadow_sync_state.json": data_dir / "shadow_sync_state.json",
        "signals_history.json": data_dir / "signals_history.json",
        "ingestion_journal.json": data_dir / "ingestion_journal.json"
    }

    print("\n[*] Live Checkpoints & JSON Artifacts:")
    for name, path in json_targets.items():
        if path.exists():
            size = path.stat().st_size
            try:
                content = json.loads(path.read_text(encoding="utf-8"))
                item_count = len(content) if isinstance(content, (dict, list)) else "N/A"
                print(f"    - '{name}': Exists (Size: {size} bytes, Key/Item Count: {item_count})")
            except Exception as ex:
                print(f"    - '{name}': Exists (Size: {size} bytes, Parse Error: {ex})")
        else:
            print(f"    - '{name}': Absent")

if __name__ == "__main__":
    inspect_live_databases()
