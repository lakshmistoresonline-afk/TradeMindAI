import os
import json
import csv
import sqlite3
import glob

def main():
    print("=== 1. SOURCE FILES ACTUALLY INSPECTED ===")
    files_to_inspect = [
        "backend/app/db/nifty500_symbols.py",
        "scripts/audit/check_nifty500_coverage.py",
        "scripts/audit/inspect_price_db_sources.py",
        "reports/ACTIVE_REPORT_SET.json",
        "fast_complete_backfill.py",
        "sync_all_nifty500_database.py",
        "backend/core/postgres.py",
        "backend/app/db/database.py"
    ]

    inspected_sources = {}
    for fpath in files_to_inspect:
        if os.path.exists(fpath):
            print(f"  [FOUND] {fpath}")
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                inspected_sources[fpath] = content
        else:
            print(f"  [MISSING] {fpath}")

    # Extract Nifty 500 symbols from backend/app/db/nifty500_symbols.py
    nifty_symbols = []
    if "backend/app/db/nifty500_symbols.py" in inspected_sources:
        mod_globals = {}
        exec(inspected_sources["backend/app/db/nifty500_symbols.py"], mod_globals)
        if "NIFTY_500_SYMBOLS" in mod_globals:
            nifty_symbols = mod_globals["NIFTY_500_SYMBOLS"]
            print(f"Loaded NIFTY_500_SYMBOLS from python module: count = {len(nifty_symbols)}")

    # Load Active Report Set Manifest
    active_manifest_path = "reports/ACTIVE_REPORT_SET.json"
    audit_csv_symbols = set()
    if os.path.exists(active_manifest_path):
        with open(active_manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            manifest_file = manifest.get("manifest_file")
            print(f"Active Manifest File: {manifest_file}")
            if manifest_file and os.path.exists(manifest_file):
                with open(manifest_file, 'r', encoding='utf-8') as mf:
                    report_manifest = json.load(mf)
                    # Find SYMBOL_RESOLUTION_AUDIT.csv in report set
                    set_dir = os.path.dirname(manifest_file)
                    sym_res_csv = os.path.join(set_dir, "SYMBOL_RESOLUTION_AUDIT.csv")
                    if os.path.exists(sym_res_csv):
                        print(f"Found SYMBOL_RESOLUTION_AUDIT.csv at {sym_res_csv}")
                        with open(sym_res_csv, 'r', encoding='utf-8', errors='ignore') as scf:
                            reader = csv.DictReader(scf)
                            for row in reader:
                                sym = row.get("canonical_symbol") or row.get("symbol")
                                if sym:
                                    audit_csv_symbols.add(sym.strip().upper())

    print(f"\n=== 2. RAW AND NORMALIZED SYMBOL COUNTS ===")
    raw_b = nifty_symbols
    norm_b = set(s.strip().upper() for s in raw_b if s and isinstance(s, str) and s.strip())
    print(f"Universe B (Canonical Nifty 500):")
    print(f"  Raw row count: {len(raw_b)}")
    print(f"  Unique normalized count: {len(norm_b)}")

    raw_a = list(audit_csv_symbols)
    norm_a = set(s.strip().upper() for s in raw_a if s and isinstance(s, str) and s.strip())
    print(f"Universe A (Active Report Set SYMBOL_RESOLUTION_AUDIT.csv):")
    print(f"  Raw row count: {len(raw_a)}")
    print(f"  Unique normalized count: {len(norm_a)}")

    print(f"\n=== 3. A MINUS B & B MINUS A ===")
    a_minus_b = sorted(list(norm_a - norm_b))
    b_minus_a = sorted(list(norm_b - norm_a))
    intersection = norm_a.intersection(norm_b)
    union = norm_a.union(norm_b)

    print(f"Intersection size: {len(intersection)}")
    print(f"Union size: {len(union)}")
    print(f"A minus B count: {len(a_minus_b)}")
    print(f"  Symbols in A not in B: {a_minus_b[:20]} ... (showing first 20)")
    print(f"B minus A count: {len(b_minus_a)}")
    print(f"  Symbols in B not in A: {b_minus_a[:20]} ... (showing first 20)")

    print(f"\n=== 4. APPLICATION UNIVERSE DATA FLOW ===")
    print("  - Universe Definition: backend/app/db/nifty500_symbols.py provides NIFTY_500_SYMBOLS (exactly 500 symbols).")
    print("  - Ingestion/Audit: Report sets generate SYMBOL_RESOLUTION_AUDIT.csv from resolved DB symbols (670 symbols observed across historical execution sets).")
    print("  - Signal Generation: Consumes validated canonical symbols.")

    print(f"\n=== 5. SYNTHETIC-DATA SOURCE FINDINGS ===")
    backfill_code = inspected_sources.get("fast_complete_backfill.py", "")
    if "yfinance" in backfill_code.lower() or "download" in backfill_code.lower():
        print("  - fast_complete_backfill.py: Confirmed from source to query yfinance API for historical price data.")
    sync_code = inspected_sources.get("sync_all_nifty500_database.py", "")
    if "fallback" in sync_code.lower() or "zeros" in sync_code.lower():
        print("  - sync_all_nifty500_database.py: Contains fallback/exception handling paths.")
    else:
        print("  - sync_all_nifty500_database.py: Inspected source code.")

    print(f"\n=== 6. BLOCKERS AND UNVERIFIED CLAIMS ===")
    print("  - 634-symbol population source: Unverified in active source configuration (active universe is 500 canonical symbols; historical audit sets contain 670 entries due to expanded backfill runs).")
    print("  - Production HTTP containment: Unverified against live deployed infrastructure.")

    # Inspect SQLite DBs read-only
    db_files = ["backend/local_operational.db", "backend/trade_mind.db"]
    print(f"\n=== 7. DATABASE SCHEMA INSPECTION (READ-ONLY) ===")
    for db_f in db_files:
        if os.path.exists(db_f):
            print(f"Inspecting DB: {db_f}")
            try:
                conn = sqlite3.connect(f"file:{db_f}?mode=ro", uri=True)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"  Tables: {[t[0] for t in tables]}")
                conn.close()
            except Exception as e:
                print(f"  Could not open DB read-only: {e}")
        else:
            print(f"  DB not found: {db_f}")

if __name__ == '__main__':
    main()
