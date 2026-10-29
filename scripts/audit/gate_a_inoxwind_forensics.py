"""
================================================================================
TradeMindAI Gate A — INOXWIND Transaction ID Forensic Analysis Script
================================================================================
Audits INOXWIND across DuckDB daily_ohlcv table source tags, ingestion journal,
checkpoint file, and INOXWIND.parquet read-only.
================================================================================
"""

import json
import duckdb
import pandas as pd
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
data_dir = root_dir / "backend" / "data"
journal_file = data_dir / "ingestion_journal.json"
checkpoint_file = data_dir / "ingestion_checkpoint.json"
duckdb_file = data_dir / "analytical.duckdb"
inox_parquet = data_dir / "features" / "INOXWIND.parquet"

def run_gate_a_audit():
    print("=== [GATE A] Fresh Read-Only INOXWIND Transaction Audit ===")

    # 1. DuckDB Source Tag Inspection
    if duckdb_file.exists():
        con = duckdb.connect(str(duckdb_file), read_only=True)
        duck_rows = con.execute("SELECT count(*), min(date), max(date), count(distinct source) FROM daily_ohlcv WHERE symbol = 'INOXWIND'").fetchone()
        source_tags = con.execute("SELECT DISTINCT source FROM daily_ohlcv WHERE symbol = 'INOXWIND'").fetchall()
        con.close()
        print(f"[*] DuckDB INOXWIND Data:")
        print(f"    - Total Rows: {duck_rows[0]}")
        print(f"    - Date Range: {duck_rows[1]} to {duck_rows[2]}")
        print(f"    - Distinct Source Tags: {[s[0] for s in source_tags]}")

    # 2. Parquet File Inspection
    if inox_parquet.exists():
        df_p = pd.read_parquet(inox_parquet)
        print(f"[*] Parquet INOXWIND.parquet Data:")
        print(f"    - Total Rows: {len(df_p)}")
        print(f"    - Date Range: {df_p['date'].min()} to {df_p['date'].max()}")

    # 3. Checkpoint Entry
    if checkpoint_file.exists():
        checkpoint_data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        inox_cp = checkpoint_data.get("INOXWIND")
        print(f"[*] Checkpoint Entry for INOXWIND:\n{json.dumps(inox_cp, indent=2)}")

    # 4. Journal Entry
    if journal_file.exists():
        journal_data = json.loads(journal_file.read_text(encoding="utf-8"))
        inox_j = journal_data.get("INOXWIND")
        print(f"[*] Journal Entry for INOXWIND:\n{json.dumps(inox_j, indent=2)}")

if __name__ == "__main__":
    run_gate_a_audit()
