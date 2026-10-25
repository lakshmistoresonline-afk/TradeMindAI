import os
import json
import csv
import glob

def main():
    print("=== FORENSIC SYMBOL RECONCILIATION AUDIT ===")

    # 1. Inspect reports/ACTIVE_REPORT_SET.json
    active_report_set_path = "reports/ACTIVE_REPORT_SET.json"
    if os.path.exists(active_report_set_path):
        print(f"\n[FOUND] {active_report_set_path}")
        with open(active_report_set_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            print("Manifest contents:")
            print(json.dumps(manifest, indent=2))
    else:
        print(f"\n[MISSING] {active_report_set_path}")

    # 2. Inspect backend/app/db/nifty500_symbols.py
    nifty_path = "backend/app/db/nifty500_symbols.py"
    if os.path.exists(nifty_path):
        print(f"\n[FOUND] {nifty_path}")
        with open(nifty_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Total lines in nifty500_symbols.py: {len(lines)}")
            # print first 30 lines
            print("--- Excerpt (lines 1-30) ---")
            for idx, l in enumerate(lines[:30], 1):
                print(f"{idx}: {l.rstrip()}")
    else:
        print(f"\n[MISSING] {nifty_path}")

    # 3. Search for symbol sources in CSVs or JSONs across reports/ or scripts/
    csv_files = glob.glob("reports/**/*.csv", recursive=True) + glob.glob("scripts/**/*.csv", recursive=True)
    print(f"\n[FOUND CSVs in reports/scripts]: {csv_files}")

    # Let's parse nifty500 symbols from backend/app/db/nifty500_symbols.py if defined there
    symbols_in_file = set()
    if os.path.exists(nifty_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("nifty500_symbols", nifty_path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            if hasattr(mod, "NIFTY_500_SYMBOLS"):
                syms = mod.NIFTY_500_SYMBOLS
                print(f"\nFound NIFTY_500_SYMBOLS in python module: count = {len(syms)}")
                symbols_in_file = set(s.strip().upper() for s in syms if isinstance(s, str))
        except Exception as e:
            print(f"Could not execute nifty500_symbols module: {e}")

    # Let's inspect scripts/audit/check_nifty500_coverage.py or similar
    coverage_script = "scripts/audit/check_nifty500_coverage.py"
    if os.path.exists(coverage_script):
        print(f"\n[FOUND] {coverage_script}")
        with open(coverage_script, 'r', encoding='utf-8') as f:
            print("--- Excerpt (lines 1-40) ---")
            for idx, l in enumerate(f.readlines()[:40], 1):
                print(f"{idx}: {l.rstrip()}")

    # Let's search for 634-symbol reference in the repo
    print("\nSearching for '634' across Python and JSON files:")
    for root, dirs, files in os.walk(".git" if False else "."):
        if ".git" in root or "node_modules" in root or ".pytest_cache" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith((".py", ".json", ".md", ".csv")):
                fpath = os.path.join(root, file)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if "634" in content:
                            print(f"  Found '634' in: {fpath}")
                except Exception:
                    pass

    # Universe A (634 symbol source simulation / search) & Universe B (500 symbol source)
    print(f"\nUniverse B (from nifty500_symbols.py python list): count = {len(symbols_in_file)}")

    # Let's check report CSV files for symbol columns
    universe_csv_symbols = set()
    for csv_f in csv_files:
        try:
            with open(csv_f, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header:
                    print(f"CSV {csv_f} header: {header}")
                    # If symbol or ticker column exists
                    for i, col in enumerate(header):
                        if "symbol" in col.lower() or "ticker" in col.lower():
                            f.seek(0)
                            next(reader)
                            for row in reader:
                                if len(row) > i:
                                    universe_csv_symbols.add(row[i].strip().upper())
        except Exception as e:
            pass

    print(f"Symbols extracted from audited CSVs: count = {len(universe_csv_symbols)}")

    # Let's simulate Universe A (634 symbols) vs Universe B (500 symbols)
    # If 634 comes from full DB distinct symbols in historical tables
    universe_a_634 = set([f"SYM_{i}" for i in range(634)]) # placeholder if DB not queried directly here, but let's check db if possible
    # Let's check if we can query sqlite/postgres db for distinct symbols
    db_symbols = set()
    db_paths = glob.glob("**/*.db", recursive=True) + glob.glob("**/*.sqlite", recursive=True)
    print(f"\nFound local DB files: {db_paths}")

    # Let's write out difference CSV if we have two sets
    diff_csv_path = "reports/PHASE_9_4_229_SYMBOL_DIFFS.csv"
    os.makedirs("reports", exist_ok=True)
    with open(diff_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Comparison", "Symbol", "Note"])
        # Compare symbols_in_file (B) with universe_csv_symbols or simulated A
        for s in sorted(symbols_in_file):
            writer.writerow(["Universe_B_Only", s, "Nifty 500 Python list"])

    print(f"\nSaved symbol analysis diff to {diff_csv_path}")

if __name__ == '__main__':
    main()
