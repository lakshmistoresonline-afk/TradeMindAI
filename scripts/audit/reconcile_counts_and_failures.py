"""
================================================================================
TradeMindAI: Count Discrepancy & Symbol Failure Forensic Audit
================================================================================
Reconciles:
- Checkpoint SUCCESS count (494)
- DuckDB Distinct Symbol count (495)
- Parquet Feature Store File count (496)
Identifies the exact extra symbols and inspects the 6 failed symbols.
================================================================================
"""

import glob
import json
import duckdb
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
data_dir = root_dir / "backend" / "data"
features_dir = data_dir / "features"
duckdb_path = data_dir / "analytical.duckdb"

def run_count_reconciliation():
    print("=== [SECTION 1] Reconciling 494 / 495 / 496 Count Discrepancy ===")

    # 1. Checkpoint
    checkpoint_file = data_dir / "ingestion_checkpoint.json"
    checkpoint_data = json.loads(checkpoint_file.read_text(encoding="utf-8")) if checkpoint_file.exists() else {}
    checkpoint_success = {s for s, v in checkpoint_data.items() if v.get("status") == "SUCCESS"}
    checkpoint_failed = {s: v.get("error") for s, v in checkpoint_data.items() if v.get("status") == "FAILED"}

    print(f"[*] Checkpoint SUCCESS symbols count: {len(checkpoint_success)}")
    print(f"[*] Checkpoint FAILED symbols count: {len(checkpoint_failed)}")
    print("    Failed symbols & errors:")
    for s, err in checkpoint_failed.items():
        print(f"    - {s}: {err}")

    # 2. Live DuckDB
    con = duckdb.connect(str(duckdb_path), read_only=True)
    duck_symbols = set(r[0] for r in con.execute("SELECT DISTINCT symbol FROM daily_ohlcv").fetchall())
    con.close()
    print(f"\n[*] DuckDB distinct symbols count: {len(duck_symbols)}")

    # 3. Live Parquet Feature Files
    parquet_files = set(Path(f).stem for f in glob.glob(str(features_dir / "*.parquet")))
    print(f"[*] Parquet feature files count: {len(parquet_files)}")

    # 4. Difference Analysis
    duck_not_in_checkpoint = duck_symbols - checkpoint_success
    parquet_not_in_checkpoint = parquet_files - checkpoint_success
    parquet_not_in_duck = parquet_files - duck_symbols
    duck_not_in_parquet = duck_symbols - parquet_files

    print(f"\n[*] Discrepancy Findings:")
    print(f"    - Symbols in DuckDB but not in Checkpoint SUCCESS: {duck_not_in_checkpoint}")
    print(f"    - Symbols in Parquet but not in Checkpoint SUCCESS: {parquet_not_in_checkpoint}")
    print(f"    - Symbols in Parquet but not in DuckDB: {parquet_not_in_duck}")
    print(f"    - Symbols in DuckDB but not in Parquet: {duck_not_in_parquet}")

if __name__ == "__main__":
    run_count_reconciliation()
