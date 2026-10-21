"""
================================================================================
TradeMindAI: PriceDB OHLCV Integrity & Canonical Universe Read-Only Audit
================================================================================
Read-only SQL inspection of historical_prices table (PriceDB) to establish:
1. Canonical Nifty 500 universe size, normalization, and uniqueness.
2. OHLCV geometric validity (high >= low, high >= open, high >= close, etc.).
3. Non-positive or null price counts.
4. Duplicate (symbol, date, source) tuples.
================================================================================
"""

import os
import sys
from sqlalchemy import func, and_, or_

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS

def inspect_ohlcv_integrity():
    print("================================================================================")
    print("  TRADEMIND AI: PriceDB OHLCV INTEGRITY & UNIVERSE READ-ONLY AUDIT")
    print("================================================================================\n")

    # 1. Canonical Universe Inspection
    print("[*] 1. Canonical Universe Inspection:")
    print(f"    - Total NIFTY_500_SYMBOLS length: {len(NIFTY_500_SYMBOLS)}")
    distinct_symbols = set(NIFTY_500_SYMBOLS)
    print(f"    - Unique normalized symbols: {len(distinct_symbols)}")
    has_whitespace = any(s != s.strip() for s in NIFTY_500_SYMBOLS)
    has_blank = any(not s for s in NIFTY_500_SYMBOLS)
    print(f"    - Has leading/trailing whitespace: {has_whitespace}")
    print(f"    - Has blank/empty symbols: {has_blank}")

    assert len(NIFTY_500_SYMBOLS) == 500
    assert len(distinct_symbols) == 500
    assert not has_whitespace
    assert not has_blank

    # 2. OHLCV Geometric & Validity Audit
    print("\n[*] 2. PriceDB OHLCV Geometric Validity Audit:")
    with SessionLocal() as session:
        total_rows = session.query(func.count(PriceDB.id)).scalar()

        invalid_high_low = session.query(func.count(PriceDB.id)).filter(PriceDB.high < PriceDB.low).scalar()
        invalid_high_open = session.query(func.count(PriceDB.id)).filter(PriceDB.high < PriceDB.open).scalar()
        invalid_high_close = session.query(func.count(PriceDB.id)).filter(PriceDB.high < PriceDB.close).scalar()
        invalid_low_open = session.query(func.count(PriceDB.id)).filter(PriceDB.low > PriceDB.open).scalar()
        invalid_low_close = session.query(func.count(PriceDB.id)).filter(PriceDB.low > PriceDB.close).scalar()
        invalid_zero_close = session.query(func.count(PriceDB.id)).filter(or_(PriceDB.close == None, PriceDB.close <= 0)).scalar()

        print(f"    - Total historical_prices rows: {total_rows}")
        print(f"    - Invalid High < Low rows: {invalid_high_low}")
        print(f"    - Invalid High < Open rows: {invalid_high_open}")
        print(f"    - Invalid High < Close rows: {invalid_high_close}")
        print(f"    - Invalid Low > Open rows: {invalid_low_open}")
        print(f"    - Invalid Low > Close rows: {invalid_low_close}")
        print(f"    - Invalid Non-Positive / Null Close rows: {invalid_zero_close}")

        # Check duplicate (symbol, date, source) tuples
        dups_query = session.query(
            PriceDB.symbol, PriceDB.date, PriceDB.source, func.count(PriceDB.id)
        ).group_by(PriceDB.symbol, PriceDB.date, PriceDB.source).having(func.count(PriceDB.id) > 1).all()

        print(f"    - Duplicate (symbol, date, source) tuples: {len(dups_query)}")

if __name__ == "__main__":
    inspect_ohlcv_integrity()
