"""
================================================================================
TradeMindAI: Symbol-Set Reconciliation & BAGMANE Investigation (Section 4)
================================================================================
Compares exact symbol sets across:
- Canonical Nifty 500 Universe (500 symbols)
- Checkpoint SUCCESS symbols (499 symbols)
- DuckDB Distinct Symbols (499 symbols)
- Parquet Feature Store Filenames (499 symbols)
Investigates BAGMANE status.
================================================================================
"""

import os
import sys
import glob
import json
import duckdb
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.db.nifty500_symbols import get_nifty_500_universe

data_dir = root_dir / "backend" / "data"
checkpoint_file = data_dir / "ingestion_checkpoint.json"
duckdb_file = data_dir / "analytical.duckdb"
features_dir = data_dir / "features"

def reconcile_symbol_sets():
    print("=== [SECTION 4] Symbol-Set Reconciliation & BAGMANE Investigation ===")

    canonical_universe = set(get_nifty_500_universe().keys())
    print(f"[*] Canonical Nifty 500 Universe Count: {len(canonical_universe)}")

    checkpoint_data = json.loads(checkpoint_file.read_text(encoding="utf-8")) if checkpoint_file.exists() else {}
    checkpoint_success = {s for s, v in checkpoint_data.items() if v.get("status") == "SUCCESS"}
    print(f"[*] Checkpoint SUCCESS Symbol Set Count: {len(checkpoint_success)}")

    con = duckdb.connect(str(duckdb_file), read_only=True)
    duck_symbols = set(r[0] for r in con.execute("SELECT DISTINCT symbol FROM daily_ohlcv").fetchall())
    con.close()
    print(f"[*] DuckDB Distinct Symbol Set Count: {len(duck_symbols)}")

    parquet_symbols = set(Path(f).stem for f in glob.glob(str(features_dir / "*.parquet")))
    print(f"[*] Parquet Feature Store Symbol Set Count: {len(parquet_symbols)}")

    # Check 1: Equality of Active Persisted Stores
    stores_equal = (checkpoint_success == duck_symbols == parquet_symbols)
    print(f"[+] Active Persisted Stores Symbol-Set Equality: {'PERFECT 100% MATCH' if stores_equal else 'MISMATCH DETECTED'}")

    # Check 2: Missing from Canonical 500 Universe
    missing_from_canonical = canonical_universe - checkpoint_success
    print(f"[*] Missing Symbols from Canonical 500 Universe ({len(missing_from_canonical)}): {missing_from_canonical}")

    # BAGMANE Investigation
    if "BAGMANE" in missing_from_canonical:
        bg_status = checkpoint_data.get("BAGMANE")
        print(f"\n[*] BAGMANE Checkpoint Status:\n{json.dumps(bg_status, indent=2)}")

if __name__ == "__main__":
    reconcile_symbol_sets()
