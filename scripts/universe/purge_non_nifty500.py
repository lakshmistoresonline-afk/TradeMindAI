"""
================================================================================
TradeMindAI: Universe Purge & Strict Nifty 500 Alignment (500 Stocks Only)
================================================================================
Purges any stocks and associated price/feature rows from the database that do not
belong to the authoritative Nifty 500 symbol list, ensuring exactly 500 stocks.
================================================================================
"""

import os
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, StockDB, PriceDB, TechnicalFeatureDB, LiveSignalDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS

def purge_non_nifty500():
    print("================================================================================")
    print("  TRADEMIND AI: UNIVERSE PURGE & STRICT NIFTY 500 ALIGNMENT (500 STOCKS)")
    print("================================================================================\n")

    n500_set = set(NIFTY_500_SYMBOLS)
    print(f"[*] Authoritative target Nifty 500 universe size: {len(n500_set)}")

    with SessionLocal() as session:
        all_stocks = session.query(StockDB).all()
        print(f"[*] Current stocks in DB: {len(all_stocks)}")

        to_delete = [s for s in all_stocks if s.symbol not in n500_set]
        print(f"[*] Purging {len(to_delete)} non-Nifty-500 stocks...")

        for stock in to_delete:
            sym = stock.symbol
            # Delete associated price history
            session.query(PriceDB).filter(PriceDB.symbol == sym).delete()
            # Delete associated technical features
            session.query(TechnicalFeatureDB).filter(TechnicalFeatureDB.symbol == sym).delete()
            # Delete associated live signals
            session.query(LiveSignalDB).filter(LiveSignalDB.symbol == sym).delete()
            # Delete stock record
            session.delete(stock)

        session.commit()

        final_stocks = session.query(StockDB).count()
        print(f"[SUCCESS] Universe purge complete. Final stock count in database: {final_stocks}")
        assert final_stocks == 500, f"Expected exactly 500 stocks, got {final_stocks}"

if __name__ == "__main__":
    purge_non_nifty500()
