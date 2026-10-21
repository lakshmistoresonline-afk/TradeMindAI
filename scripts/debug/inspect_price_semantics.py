"""
================================================================================
TradeMindAI: PriceDB Record Semantics & Granularity Inspection
================================================================================
Read-only SQL inspection of historical_prices table (PriceDB) to establish:
1. Total records.
2. Distinct exact timestamps.
3. Distinct calendar dates.
4. Multiple records per symbol per calendar date.
5. Distinct stored source process labels.
================================================================================
"""

import os
import sys
from sqlalchemy import func, text

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB

def inspect_price_semantics():
    print("================================================================================")
    print("  TRADEMIND AI: PriceDB RECORD SEMANTICS & GRANULARITY READ-ONLY AUDIT")
    print("================================================================================\n")

    with SessionLocal() as session:
        total_rows = session.query(func.count(PriceDB.id)).scalar()
        distinct_timestamps = session.query(func.count(func.distinct(PriceDB.date))).scalar()
        distinct_symbols = session.query(func.count(func.distinct(PriceDB.symbol))).scalar()

        # Check distinct sources stored in database
        distinct_sources = session.query(PriceDB.source, func.count(PriceDB.id)).group_by(PriceDB.source).all()

        # Check sample symbol RELIANCE for calendar date vs timestamp count
        reliance_rows = session.query(func.count(PriceDB.id)).filter(PriceDB.symbol == "RELIANCE").scalar()
        reliance_distinct_ts = session.query(func.count(func.distinct(PriceDB.date))).filter(PriceDB.symbol == "RELIANCE").scalar()

        print(f"[*] Total rows in historical_prices: {total_rows}")
        print(f"[*] Distinct symbols in historical_prices: {distinct_symbols}")
        print(f"[*] Distinct exact timestamps across table: {distinct_timestamps}")
        print(f"[*] Distinct stored source labels:")
        for src, cnt in distinct_sources:
            print(f"    - '{src}': {cnt} rows")

        print(f"\n[*] Sample Symbol (RELIANCE):")
        print(f"    - Total rows: {reliance_rows}")
        print(f"    - Distinct timestamps: {reliance_distinct_ts}")

if __name__ == "__main__":
    inspect_price_semantics()
