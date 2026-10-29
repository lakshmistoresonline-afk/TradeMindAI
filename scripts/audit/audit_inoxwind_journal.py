"""
================================================================================
TradeMindAI: Forensic INOXWIND Transaction Audit Script (Section 2)
================================================================================
Audits INOXWIND across ingestion_journal.json, ingestion_checkpoint.json,
DuckDB daily_ohlcv table, and backend/data/features/INOXWIND.parquet read-only.
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

def audit_inoxwind():
    print("=== [SECTION 2] Forensic INOXWIND Transaction Audit ===")

    # 1. Journal Inspection
    if journal_file.exists():
        journal_data = json.loads(journal_file.read_text(encoding="utf-8"))
        inox_journal = journal_data.get("INOXWIND")
        print(f"[*] Journal INOXWIND Entry:\n{json.dumps(inox_journal, indent=2)}")
    else:
        inox_journal = None
        print("[-] Journal file missing.")

    # 2. Checkpoint Inspection
    if checkpoint_file.exists():
        checkpoint_data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        inox_checkpoint = checkpoint_data.get("INOXWIND")
        print(f"[*] Checkpoint INOXWIND Entry:\n{json.dumps(inox_checkpoint, indent=2)}")

    # 3. DuckDB Inspection
    if duckdb_file.exists():
        con = duckdb.connect(str(duckdb_file), read_only=True)
        duck_rows = con.execute("SELECT date, open, high, low, close, volume, source FROM daily_ohlcv WHERE symbol = 'INOXWIND' ORDER BY date").df()
        con.close()
        print(f"[*] DuckDB INOXWIND Row Count: {len(duck_rows)}")
        if not duck_rows.empty:
            print(f"    - Earliest Date: {duck_rows['date'].min()}, Latest Date: {duck_rows['date'].max()}")
            sources = duck_rows["source"].unique()
            print(f"    - Transaction Source Tags: {list(sources)}")

    # 4. Parquet Inspection
    if inox_parquet.exists():
        df_p = pd.read_parquet(inox_parquet)
        print(f"[*] Parquet INOXWIND Row Count: {len(df_p)}")
        print(f"    - Earliest Date: {df_p['date'].min()}, Latest Date: {df_p['date'].max()}")
    else:
        print("[-] INOXWIND.parquet missing.")

    # 5. Staged Path Reference Audit
    staged_path_ref = inox_journal.get("staged_parquet_path") if isinstance(inox_journal, dict) else None
    if staged_path_ref:
        staged_exists = Path(staged_path_ref).exists()
        print(f"[*] Staged Path Referenced in Journal ('{staged_path_ref}'): Exists = {staged_exists}")

if __name__ == "__main__":
    audit_inoxwind()
