import os
import json
import csv
import sqlite3
import ast
import glob

def main():
    print("=== PHASE 9.4.231: DETAILED SYMBOL & PIPELINE FORENSICS ===")

    # 1. Inspect backend/app/db/nifty500_symbols.py contents
    nifty_path = "backend/app/db/nifty500_symbols.py"
    universe_b_symbols = set()
    if os.path.exists(nifty_path):
        print(f"\n[FOUND] {nifty_path}")
        with open(nifty_path, 'r', encoding='utf-8') as f:
            code_text = f.read()
            # Let's inspect globals by executing in a safe isolated dict or ast
            local_ns = {}
            exec(code_text, local_ns)
            for k, v in local_ns.items():
                if isinstance(v, (list, tuple, set)) and len(v) > 0 and isinstance(list(v)[0], str):
                    print(f"  Found symbol collection variable '{k}': count = {len(v)}")
                    if len(v) >= 450:
                        universe_b_symbols = set(s.strip().upper() for s in v if isinstance(s, str))

    print(f"Universe B (Canonical Nifty 500): count = {len(universe_b_symbols)}")

    # 2. Extract Universe A from SYMBOL_RESOLUTION_AUDIT.csv
    universe_a_symbols = set()
    sym_res_csv = "reports/SET_F9C02637EC04_1792649091/SYMBOL_RESOLUTION_AUDIT.csv"
    if os.path.exists(sym_res_csv):
        with open(sym_res_csv, 'r', encoding='utf-8', errors='ignore') as scf:
            reader = csv.DictReader(scf)
            for row in reader:
                sym = row.get("canonical_symbol") or row.get("symbol")
                if sym:
                    universe_a_symbols.add(sym.strip().upper())

    print(f"Universe A (Active Report Set Audit CSV): count = {len(universe_a_symbols)}")

    # 3. Set Reconciliation
    if universe_a_symbols and universe_b_symbols:
        inter = universe_a_symbols.intersection(universe_b_symbols)
        a_minus_b = sorted(list(universe_a_symbols - universe_b_symbols))
        b_minus_a = sorted(list(universe_b_symbols - universe_a_symbols))
        print(f"\n=== SET RECONCILIATION ===")
        print(f"Universe A size: {len(universe_a_symbols)}")
        print(f"Universe B size: {len(universe_b_symbols)}")
        print(f"Intersection size: {len(inter)}")
        print(f"A minus B size: {len(a_minus_b)}")
        print(f"  List A-B: {a_minus_b}")
        print(f"B minus A size: {len(b_minus_a)}")
        print(f"  List B-A: {b_minus_a}")
    else:
        print(f"\n[BLOCKED] Set reconciliation incomplete.")

if __name__ == '__main__':
    main()
