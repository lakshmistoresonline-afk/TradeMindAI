"""
================================================================================
TradeMindAI: Universe Purge & Strict Nifty 500 Alignment (500 Stocks Only)
================================================================================
Purges any stocks and associated price/feature rows from the database that do not
belong to the authoritative Nifty 500 symbol list, ensuring exactly 500 stocks.
Enforces dry-run safety by default.
================================================================================
"""

import os
import sys
import argparse

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, StockDB, PriceDB, TechnicalFeatureDB, LiveSignalDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS, validate_nifty500_universe

def purge_non_nifty500(dry_run: bool = True, force: bool = False):
    print("================================================================================")
    print("  TRADEMIND AI: UNIVERSE PURGE & STRICT NIFTY 500 ALIGNMENT (500 STOCKS)")
    print("================================================================================\n")

    validate_nifty500_universe(NIFTY_500_SYMBOLS)
    n500_set = set(NIFTY_500_SYMBOLS)
    print(f"[*] Authoritative target Nifty 500 universe size: {len(n500_set)}")

    confirm_env = os.getenv("CONFIRM_PURGE", "false").lower() == "true"
    should_execute = (not dry_run or force or confirm_env)

    with SessionLocal() as session:
        all_stocks = session.query(StockDB).all()
        print(f"[*] Current stocks in DB: {len(all_stocks)}")

        to_delete = [s for s in all_stocks if s.symbol not in n500_set]
        print(f"[*] Identified {len(to_delete)} non-Nifty-500 stocks for purging.")

        if not should_execute:
            print(f"\n[SAFETY GUARD] DRY_RUN=True. Previews deletion of {len(to_delete)} non-canonical stock records.")
            print("               To execute deletions, call purge_non_nifty500(dry_run=False, force=True) or set CONFIRM_PURGE=true.")
            return

        for stock in to_delete:
            sym = stock.symbol
            session.query(PriceDB).filter(PriceDB.symbol == sym).delete()
            session.query(TechnicalFeatureDB).filter(TechnicalFeatureDB.symbol == sym).delete()
            session.query(LiveSignalDB).filter(LiveSignalDB.symbol == sym).delete()
            session.delete(stock)

        session.commit()

        final_stocks = session.query(StockDB).count()
        print(f"[SUCCESS] Universe purge complete. Final stock count in database: {final_stocks}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Purge Non-Nifty-500 Stocks with Dry Run Safety Guard")
    parser.add_argument("--execute", action="store_true", help="Execute actual database deletes (default is dry run)")
    args = parser.parse_args()
    purge_non_nifty500(dry_run=not args.execute, force=args.execute)
