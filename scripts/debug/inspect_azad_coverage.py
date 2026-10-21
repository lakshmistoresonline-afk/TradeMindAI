"""
================================================================================
TradeMindAI: AZAD Engineering Coverage & Symbol Mapping Inspection
================================================================================
Read-only SQL query on PriceDB (historical_prices) to locate stored price records
for Azad Engineering Limited under 'AZAD', ' Azad Engineering', or other aliases.
================================================================================
"""

import os
import sys
from sqlalchemy import func, text

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB

def inspect_azad_coverage():
    print("================================================================================")
    print("  TRADEMIND AI: AZAD ENGINEERING COVERAGE READ-ONLY SQL INSPECTION")
    print("================================================================================\n")

    with SessionLocal() as session:
        # Search exact symbols and LIKE patterns
        patterns = ["AZAD", "%AZAD%", "%Azad%"]
        print("[*] Searching historical_prices for AZAD variations...")

        results = session.query(
            PriceDB.symbol,
            func.count(PriceDB.id),
            func.min(PriceDB.date),
            func.max(PriceDB.date)
        ).filter(PriceDB.symbol.ilike("%azad%")).group_by(PriceDB.symbol).all()

        if results:
            print("[+] Found PriceDB records for AZAD variations:")
            for sym, cnt, min_dt, max_dt in results:
                print(f"    - Symbol in DB: repr({repr(sym)}) | Total Rows: {cnt} | Range: {min_dt} to {max_dt}")
        else:
            print("[-] No records matching 'azad' found in historical_prices table.")

        # Check StockDB
        from backend.core.postgres import StockDB
        stocks = session.query(StockDB).filter(StockDB.symbol.ilike("%azad%")).all()
        if stocks:
            print("\n[+] Found StockDB entries for AZAD variations:")
            for st in stocks:
                print(f"    - Symbol in StockDB: repr({repr(st.symbol)}) | Name: {st.name}")
        else:
            print("\n[-] No entries matching 'azad' found in stocks table.")

if __name__ == "__main__":
    inspect_azad_coverage()
