"""
================================================================================
TradeMindAI Gate A — INOXWIND Lifecycle Trace Script
================================================================================
Performs a fresh, read-only forensic trace of INOXWIND transaction identifiers:
- Failed journal tx_id: 12adf270c32e
- Successful DuckDB source tag: TX_a1d391b2e9db
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

def run_gate_a_trace():
    print("=== [GATE A] Read-Only INOXWIND Identifier Lifecycle Trace ===")

    # 1. DuckDB Source Tag Query
    con = duckdb.connect(str(duckdb_file), read_only=True)
    tags_query = con.execute("SELECT source, count(*), min(date), max(date) FROM daily_ohlcv WHERE symbol = 'INOXWIND' GROUP BY source").fetchall()
    con.close()
    print(f"[*] DuckDB INOXWIND Source Tags:\n    {tags_query}")

    # 2. Checkpoint State Query
    cp_data = json.loads(checkpoint_file.read_text(encoding="utf-8")) if checkpoint_file.exists() else {}
    inox_cp = cp_data.get("INOXWIND")
    print(f"[*] Checkpoint INOXWIND Entry:\n    {json.dumps(inox_cp, indent=2)}")

    # 3. Journal State Query
    j_data = json.loads(journal_file.read_text(encoding="utf-8")) if journal_file.exists() else {}
    inox_j = j_data.get("INOXWIND")
    print(f"[*] Journal INOXWIND Entry:\n    {json.dumps(inox_j, indent=2)}")

    # 4. Parquet Metadata Query
    if inox_parquet.exists():
        df_p = pd.read_parquet(inox_parquet)
        print(f"[*] Parquet INOXWIND.parquet:\n    - Rows: {len(df_p)}, Date Range: {df_p['date'].min()} to {df_p['date'].max()}")

if __name__ == "__main__":
    run_gate_a_trace()
