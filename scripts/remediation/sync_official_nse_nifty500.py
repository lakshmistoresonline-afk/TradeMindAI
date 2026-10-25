"""
================================================================================
TradeMindAI: Sync Official NSE Nifty 500 List & Prune Legacy Delisted Equities
================================================================================
Downloads current official Nifty 500 index constituent CSV from NSE India.
Filters out any synthetic pattern matches.
Updates nifty500_symbols.py with the official active 500 equities.
================================================================================
"""

import os
import sys
import csv
import sqlite3
import urllib.request
import logging

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = r"D:\TradeMindAI\backend\local_operational.db"
NIFTY_CSV_URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

def fetch_official_nse_nifty500():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(NIFTY_CSV_URL, headers=headers)
    synthetic_patterns = ["N500_", "DUMMY", "SYNTHETIC", "TEMP_", "FILLER"]

    with urllib.request.urlopen(req) as response:
        lines = [line.decode("utf-8") for line in response.readlines()]
        reader = csv.DictReader(lines)
        nse_symbols = []
        seen = set()
        for row in reader:
            sym = row.get("Symbol", "").strip().upper()
            name = row.get("Company Name", "").strip()

            # Filter out synthetic words
            is_synthetic = any(p in sym for p in synthetic_patterns)
            if sym and not is_synthetic and sym not in seen:
                seen.add(sym)
                nse_symbols.append((sym, name))
                if len(nse_symbols) == 500:
                    break
        return nse_symbols

def sync_and_prune():
    logger.info("=== Step 1: Fetching Official Current NSE Nifty 500 List ===")
    official_500 = fetch_official_nse_nifty500()
    assert len(official_500) == 500, f"Expected 500 equities, got {len(official_500)}"
    logger.info(f"[+] Downloaded official NSE list: {len(official_500)} clean equities.")

    active_symbols_set = {sym for sym, _ in official_500}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update nifty500_symbols.py
    logger.info("=== Step 2: Updating backend/app/db/nifty500_symbols.py with Official 500 List ===")
    update_nifty500_symbols_file(official_500)

    # Insert or update official 500 active stocks in stocks table
    logger.info("=== Step 3: Updating stocks Directory with 500 Official Active Equities ===")
    for sym, name in official_500:
        cursor.execute("SELECT symbol FROM stocks WHERE trim(symbol) = ?;", (sym,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO stocks (symbol, name, ai_status) VALUES (?, ?, 'PENDING');", (sym, name))
        else:
            cursor.execute("UPDATE stocks SET name = ? WHERE trim(symbol) = ?;", (name, sym))

    conn.commit()
    conn.close()

def update_nifty500_symbols_file(official_500):
    symbols_file = os.path.join(base_dir, "backend", "app", "db", "nifty500_symbols.py")

    formatted_companies = ",\n    ".join([f'("{sym}", "{name.replace(chr(34), "")}")' for sym, name in official_500])

    content = f'''"""
================================================================================
TradeMindAI: Authoritative Nifty 500 Real Stock Symbols Universe (500 Equities)
================================================================================
Provides exactly 500 authentic NSE equity symbols comprising the Nifty 500 index.
Synthetic filler symbols are strictly forbidden.
Updated dynamically from official NSE ind_nifty500list.csv publication.
================================================================================
"""

def validate_nifty500_universe(symbols: list) -> bool:
    """
    Strict canonical Nifty 500 universe validator.
    Requires exactly 500 unique, valid, non-synthetic NSE equity symbols.
    """
    if not symbols or len(symbols) != 500:
        raise ValueError(f"CRITICAL UNIVERSE VALIDATION FAILURE: Nifty 500 universe must contain exactly 500 constituents (got {{len(symbols) if symbols else 0}}).")

    unique_symbols = set(symbols)
    if len(unique_symbols) != 500:
        raise ValueError(f"CRITICAL UNIVERSE VALIDATION FAILURE: Duplicate symbols detected in Nifty 500 universe ({{500 - len(unique_symbols)}} duplicates).")

    synthetic_patterns = ["N500_", "DUMMY", "SYNTHETIC", "TEMP_", "FILLER"]
    for s in symbols:
        if not s or not isinstance(s, str) or not s.strip():
            raise ValueError("CRITICAL UNIVERSE VALIDATION FAILURE: Blank or null symbol string in Nifty 500 universe.")
        s_upper = s.strip().upper()
        for p in synthetic_patterns:
            if p in s_upper:
                raise ValueError(f"CRITICAL UNIVERSE VALIDATION FAILURE: Synthetic filler pattern '{{p}}' detected in symbol '{{s}}'. Synthetic symbols are forbidden.")

    return True

def get_nifty_500_universe() -> dict:
    d = {{}}
    for sym, name in raw_companies:
        s_clean = sym.strip().upper()
        if s_clean and s_clean not in d:
            d[s_clean] = name.strip()

    res = {{k: d[k] for k in list(d.keys())[:500]}}
    validate_nifty500_universe(list(res.keys()))
    return res

raw_companies = [
    {formatted_companies}
]

NIFTY_500_SYMBOLS = [s.strip().upper() for s in get_nifty_500_universe().keys() if s and s.strip()]
'''

    with open(symbols_file, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"[SUCCESS] Updated {symbols_file} with 500 official active NSE equities.")

if __name__ == "__main__":
    sync_and_prune()
