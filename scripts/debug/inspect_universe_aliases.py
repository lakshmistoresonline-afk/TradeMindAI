"""
================================================================================
TradeMindAI: Full Nifty 500 Symbol Alias & Unmatched Symbol Audit
================================================================================
Compares canonical NIFTY_500_SYMBOLS against distinct symbols in PriceDB
to identify all stored symbol variations, aliases, and un-normalized strings.
================================================================================
"""

import os
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS

def inspect_universe_aliases():
    print("================================================================================")
    print("  TRADEMIND AI: FULL UNIVERSE SYMBOL ALIAS & UNMATCHED SYMBOL READ-ONLY AUDIT")
    print("================================================================================\n")

    with SessionLocal() as session:
        db_symbols_raw = [r[0] for r in session.query(PriceDB.symbol).distinct().all() if r[0]]
        db_symbols_set = set(db_symbols_raw)
        db_symbols_normalized = {s.strip().upper(): s for s in db_symbols_raw}

        canonical_set = set(NIFTY_500_SYMBOLS)
        missing_exact = []
        resolved_alias = {}

        for sym in NIFTY_500_SYMBOLS:
            if sym in db_symbols_set:
                continue # Exact match
            elif sym in db_symbols_normalized:
                raw_match = db_symbols_normalized[sym]
                resolved_alias[sym] = raw_match
            else:
                missing_exact.append(sym)

        print(f"[*] Total canonical symbols: {len(canonical_set)}")
        print(f"[*] Distinct raw symbols in PriceDB: {len(db_symbols_set)}")
        print(f"[*] Canonical symbols with exact match in PriceDB: {len(canonical_set) - len(missing_exact) - len(resolved_alias)}")
        print(f"[*] Canonical symbols resolved via alias/whitespace mapping: {len(resolved_alias)}")
        for k, v in resolved_alias.items():
            print(f"    - Canonical '{k}' -> Stored in PriceDB as {repr(v)}")

        print(f"[*] Unmatched canonical symbols (0 records in PriceDB): {len(missing_exact)}")
        if missing_exact:
            print(f"    Unmatched: {missing_exact}")

if __name__ == "__main__":
    inspect_universe_aliases()
