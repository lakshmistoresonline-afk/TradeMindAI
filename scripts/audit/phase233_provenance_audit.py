import os
import json
import csv
import sqlite3
import glob

def main():
    print("=== PHASE 9.4.233: SYMBOL UNIVERSE & PROVENANCE FORENSICS ===")

    # 1. Inspect backend/app/db/nifty500_symbols.py
    nifty_path = "backend/app/db/nifty500_symbols.py"
    universe_b_symbols = set()
    if os.path.exists(nifty_path):
        print(f"\n[FOUND] {nifty_path}")
        with open(nifty_path, 'r', encoding='utf-8') as f:
            code_text = f.read()
            local_ns = {}
            exec(code_text, local_ns)
            for k, v in local_ns.items():
                if isinstance(v, (list, tuple, set)) and len(v) > 0 and isinstance(list(v)[0], str):
                    if len(v) >= 450:
                        universe_b_symbols = set(s.strip().upper() for s in v if isinstance(s, str))
        print(f"  Canonical Nifty 500 (Universe B) count: {len(universe_b_symbols)}")

    # 2. Inspect active report set SYMBOL_RESOLUTION_AUDIT.csv (Universe A)
    universe_a_symbols = set()
    sym_res_csv = "reports/SET_F9C02637EC04_1792649091/SYMBOL_RESOLUTION_AUDIT.csv"
    if os.path.exists(sym_res_csv):
        print(f"\n[FOUND] {sym_res_csv}")
        with open(sym_res_csv, 'r', encoding='utf-8', errors='ignore') as scf:
            reader = csv.DictReader(scf)
            for row in reader:
                sym = row.get("canonical_symbol") or row.get("symbol")
                if sym:
                    universe_a_symbols.add(sym.strip().upper())
        print(f"  Active Report Set Audit CSV (Universe A) count: {len(universe_a_symbols)}")

    # 3. Set Reconciliation
    if universe_a_symbols and universe_b_symbols:
        inter = universe_a_symbols.intersection(universe_b_symbols)
        a_minus_b = sorted(list(universe_a_symbols - universe_b_symbols))
        b_minus_a = sorted(list(universe_b_symbols - universe_a_symbols))
        print(f"\n=== SET RECONCILIATION (Universe A vs Universe B) ===")
        print(f"  Intersection size: {len(inter)}")
        print(f"  A minus B size: {len(a_minus_b)} (Examples: {a_minus_b[:10]})")
        print(f"  B minus A size: {len(b_minus_a)} (Examples: {b_minus_a[:10]})")

    # 4. Inspect SQLite DB for historical prices distinct symbols & row counts
    db_path = "backend/local_operational.db"
    if os.path.exists(db_path):
        print(f"\n[FOUND DB] {db_path}")
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT symbol) FROM historical_prices;")
            total_bars, distinct_syms = cursor.fetchone()
            print(f"  historical_prices: total bars = {total_bars}, distinct symbols = {distinct_syms}")

            cursor.execute("SELECT symbol, COUNT(*) as cnt FROM historical_prices GROUP BY symbol ORDER BY cnt DESC LIMIT 10;")
            top_syms = cursor.fetchall()
            print(f"  Top symbols by bar count: {top_syms}")

            conn.close()
        except Exception as e:
            print(f"  DB error: {e}")

    # 5. Search for backfill scripts and check source code references
    backfill_scripts = glob.glob("scripts/data/backfill_*.py") + glob.glob("scripts/data/fast_complete_backfill.py") + glob.glob("backend/services/historical_backfill_service.py")
    print(f"\n[FOUND BACKFILL SCRIPTS]: {backfill_scripts}")
    for bf in backfill_scripts:
        if os.path.exists(bf):
            print(f"  Inspecting {bf}:")
            with open(bf, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print(f"    Total lines: {len(lines)}")
                for idx, l in enumerate(lines[:15], 1):
                    print(f"      {idx}: {l.rstrip()}")

if __name__ == '__main__':
    main()
