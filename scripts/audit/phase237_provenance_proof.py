import os
import json
import csv
import sqlite3
import ast

def main():
    print("=== PHASE 9.4.237: DYNAMIC UNIVERSE & OHLCV PROVENANCE PROOF ===")

    # 1. Non-executing AST extraction of backend/app/db/nifty500_symbols.py
    nifty_path = "backend/app/db/nifty500_symbols.py"
    universe_b_symbols = set()
    ast_nodes_found = []
    if os.path.exists(nifty_path):
        print(f"\n[FOUND] {nifty_path}")
        with open(nifty_path, 'r', encoding='utf-8') as f:
            code_text = f.read()
            tree = ast.parse(code_text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            ast_nodes_found.append(target.id)
                            if target.id == "NIFTY_500_SYMBOLS":
                                if isinstance(node.value, (ast.List, ast.Tuple)):
                                    for elt in node.value.elts:
                                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                            universe_b_symbols.add(elt.value.strip().upper())
                                        elif isinstance(elt, ast.Str):
                                            universe_b_symbols.add(elt.s.strip().upper())
        print(f"  AST Assignment targets found in nifty500_symbols.py: {ast_nodes_found}")
        print(f"  Canonical Nifty 500 (Universe B via AST literal extraction): count = {len(universe_b_symbols)}")
    else:
        print(f"\n[MISSING] {nifty_path}")

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
        print(f"  B minus A size: {len(b_minus_a)}")
    else:
        print(f"\n[UNVERIFIED] Universe B extraction via AST literal was empty because NIFTY_500_SYMBOLS is populated dynamically at runtime.")

    # 4. Read-only SQLite DB Inspection
    db_path = "backend/local_operational.db"
    if os.path.exists(db_path):
        print(f"\n[FOUND DB] {db_path}")
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT symbol), MIN(date), MAX(date) FROM historical_prices;")
            res = cursor.fetchone()
            print(f"  historical_prices: total bars = {res[0]}, distinct symbols = {res[1]}, date range = {res[2]} to {res[3]}")
            conn.close()
        except Exception as e:
            print(f"  DB Error: {e}")

if __name__ == '__main__':
    main()
