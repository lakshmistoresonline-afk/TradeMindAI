"""
================================================================================
TradeMindAI Phase A — Forensic Pre-Ingestion Database & Pipeline Audit
================================================================================
Queries live active DuckDB, backup snapshot DuckDB, live Parquet feature stores,
active checkpoints, and configuration read-only before executing Phase B/C.
================================================================================
"""

import os
import duckdb
import pandas as pd
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
data_dir = root_dir / "backend" / "data"
features_dir = data_dir / "features"
live_db = data_dir / "analytical.duckdb"
backup_db = data_dir / "backup_snapshot_r4640" / "analytical.duckdb"

def run_phase_a_audit():
    print("=== [PHASE A] Starting Forensic Audit Before Ingestion ===")

    # 1. Audit Live DuckDB
    print(f"\n1. Live Active DuckDB Inspection ({live_db}):")
    if live_db.exists():
        con = duckdb.connect(str(live_db), read_only=True)
        tables = con.execute("SHOW TABLES").fetchall()
        print(f"   - Tables found: {[t[0] for t in tables]}")
        for t in tables:
            t_name = t[0]
            cnt = con.execute(f"SELECT count(*) FROM {t_name}").fetchone()[0]
            distinct_syms = con.execute(f"SELECT count(distinct symbol) FROM {t_name}").fetchone()[0] if "symbol" in [c[0] for c in con.execute(f"DESCRIBE {t_name}").fetchall()] else "N/A"
            print(f"   - Table '{t_name}': {cnt} total rows, {distinct_syms} distinct symbols")
        con.close()
    else:
        print("   - Live DuckDB does not exist.")

    # 2. Audit Backup Snapshot DuckDB
    print(f"\n2. Backup Snapshot DuckDB Inspection ({backup_db}):")
    if backup_db.exists():
        con = duckdb.connect(str(backup_db), read_only=True)
        tables = con.execute("SHOW TABLES").fetchall()
        print(f"   - Tables found: {[t[0] for t in tables]}")
        for t in tables:
            t_name = t[0]
            cnt = con.execute(f"SELECT count(*) FROM {t_name}").fetchone()[0]
            rows = con.execute(f"SELECT symbol, count(*), min(date), max(date) FROM {t_name} GROUP BY symbol ORDER BY symbol").fetchall()
            print(f"   - Table '{t_name}': {cnt} total rows across {len(rows)} symbols:")
            for sym, scnt, smin, smax in rows:
                print(f"     * {sym}: {scnt} rows ({smin} to {smax})")
        con.close()
    else:
        print("   - Backup DuckDB does not exist.")

    # 3. Audit Live Parquet Feature Store
    live_parquets = list(features_dir.glob("*.parquet")) if features_dir.exists() else []
    print(f"\n3. Live Parquet Feature Store Directory ({features_dir}):")
    print(f"   - Total .parquet files present: {len(live_parquets)}")

    # 4. Audit Safety Invariants in Configuration
    print("\n4. Safety Invariants Configuration Check:")
    try:
        from backend.core.config import settings
        print(f"   - REAL_TRADING: {settings.REAL_TRADING}")
        print(f"   - LIVE_EXECUTION_ENABLED: {settings.LIVE_EXECUTION_ENABLED}")
        print(f"   - BROKER_ORDER_EXECUTION_ENABLED: {settings.BROKER_ORDER_EXECUTION_ENABLED}")
        print(f"   - QUARANTINE_ACTIVE: {settings.QUARANTINE_ACTIVE}")
    except Exception as ex:
        print(f"   - Error inspecting settings: {ex}")

if __name__ == "__main__":
    run_phase_a_audit()
