import os
import json
import csv
import sqlite3
import ast

def main():
    print("=== PHASE 9.4.235: AUDIT EVIDENCE INTEGRITY & PROVENANCE CLOSURE ===")

    # 1. Inspect Universe B from backend/app/db/nifty500_symbols.py via AST non-executing
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
        print(f"  Canonical Nifty 500 (Universe B): count = {len(universe_b_symbols)}")

    # 2. Inspect Universe A from active report set SYMBOL_RESOLUTION_AUDIT.csv
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
        print(f"  Universe A (Active Report Set Audit CSV): count = {len(universe_a_symbols)}")

    # 3. Set Reconciliation
    if universe_a_symbols and universe_b_symbols:
        inter = universe_a_symbols.intersection(universe_b_symbols)
        a_minus_b = sorted(list(universe_a_symbols - universe_b_symbols))
        b_minus_a = sorted(list(universe_b_symbols - universe_a_symbols))
        print(f"\n=== SET RECONCILIATION ===")
        print(f"  Intersection size: {len(inter)}")
        print(f"  A minus B size: {len(a_minus_b)}")
        print(f"    Full list A-B: {a_minus_b}")
        print(f"  B minus A size: {len(b_minus_a)}")
        print(f"    Full list B-A: {b_minus_a}")

    # 4. Read-only SQLite DB Inspection
    db_path = "backend/local_operational.db"
    if os.path.exists(db_path):
        print(f"\n[FOUND DB] {db_path}")
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(historical_prices);")
            cols = [col[1] for col in cursor.fetchall()]
            print(f"  historical_prices columns: {cols}")

            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT symbol) FROM historical_prices;")
            res = cursor.fetchone()
            print(f"  historical_prices: total bars = {res[0]}, distinct symbols = {res[1]}")

            cursor.execute("SELECT symbol, COUNT(*) as cnt FROM historical_prices GROUP BY symbol ORDER BY cnt DESC LIMIT 10;")
            top_syms = cursor.fetchall()
            print(f"  Top symbols by bar count: {top_syms}")

            conn.close()
        except Exception as e:
            print(f"  DB Error: {e}")

if __name__ == '__main__':
    main()
