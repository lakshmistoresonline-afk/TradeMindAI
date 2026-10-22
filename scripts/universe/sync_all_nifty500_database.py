"""
================================================================================
TradeMindAI: Full Nifty 500 Database Sync & Price Backfill (500 Equities)
================================================================================
Syncs database stocks and price history using authentic market data source adapters.
Synthetic price generation is strictly forbidden. Missing history remains missing.
================================================================================
"""

import os
import sys
import datetime
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.core.postgres import DATABASE_URL, SessionLocal, StockDB, PriceDB
from backend.app.db.nifty500_symbols import get_nifty_500_universe, validate_nifty500_universe
from backend.services.historical_backfill_service import HistoricalBackfillService

def sync_database_to_nifty500():
    print("================================================================================")
    print("  TRADEMIND AI: FULL NIFTY 500 DATABASE SYNC (500 EQUITIES)")
    print("================================================================================\n")

    universe_dict = get_nifty_500_universe()
    symbols = list(universe_dict.keys())
    validate_nifty500_universe(symbols)
    print(f"[*] Target Nifty 500 Universe: exactly {len(symbols)} authentic constituents.")

    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2026, 10, 17)

    added_count = 0
    with SessionLocal() as session:
        existing_stocks = {s.symbol for s in session.query(StockDB).all()}
        new_stocks = []
        for sym, name in universe_dict.items():
            if sym not in existing_stocks:
                new_stocks.append(StockDB(
                    symbol=sym,
                    name=name,
                    index_membership="NIFTY_500",
                    universe_version="NIFTY_500_CANONICAL",
                    ai_status="OPERATIONAL",
                    updated_at=datetime.utcnow()
                ))
                added_count += 1
            else:
                stk = session.query(StockDB).filter(StockDB.symbol == sym).first()
                if stk and stk.index_membership != "NIFTY_500":
                    stk.index_membership = "NIFTY_500"

        if new_stocks:
            session.bulk_save_objects(new_stocks)
            session.commit()
            print(f"   [+] Added {added_count} missing Nifty 500 stocks to master stock registry.")

        all_stocks = session.query(StockDB).all()
        print(f"[*] Auditing price history from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} for {len(all_stocks)} stocks...")

        for stock in all_stocks:
            sym = stock.symbol
            existing_cnt = session.query(PriceDB.date).filter(PriceDB.symbol == sym).count()
            if existing_cnt == 0:
                print(f"   [+] Fetching authentic market history for {sym}...")
                bars = HistoricalBackfillService.fetch_authentic_source_bars(sym, start_date, end_date)
                if bars:
                    db_objects = [PriceDB(
                        symbol=b["symbol"], date=b["date"], open=b["open"], high=b["high"],
                        low=b["low"], close=b["close"], volume=b["volume"], source=b["source"]
                    ) for b in bars]
                    session.bulk_save_objects(db_objects)
                    session.commit()
                    print(f"       -> Added {len(db_objects)} authentic price bars for {sym}.")

    print("[SUCCESS] Full Nifty 500 database sync completed successfully!")

if __name__ == "__main__":
    sync_database_to_nifty500()
