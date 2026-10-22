"""
================================================================================
TradeMindAI: Fast Nifty 500 Price Backfill Engine
================================================================================
Fetches authentic price history for Nifty 500 constituent stocks from 2015 to present.
Synthetic sine-wave price generation is strictly forbidden. Missing data remains missing.
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

def run_fast_nifty500_backfill():
    print("================================================================================")
    print("  TRADEMIND AI: AUTHENTIC NIFTY 500 PRICE BACKFILL ENGINE")
    print("================================================================================\n")

    universe_dict = get_nifty_500_universe()
    symbols = list(universe_dict.keys())
    validate_nifty500_universe(symbols)
    print(f"[*] Universe: exactly {len(symbols)} authentic Nifty 500 constituents.")

    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2026, 10, 17)

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
        if new_stocks:
            session.bulk_save_objects(new_stocks)
            session.commit()

        all_stocks = session.query(StockDB).all()
        print(f"[*] Backfilling authentic market price records for {len(all_stocks)} stocks...")

        for stock in all_stocks:
            sym = stock.symbol
            existing_cnt = session.query(PriceDB.date).filter(PriceDB.symbol == sym).count()
            if existing_cnt == 0:
                bars = HistoricalBackfillService.fetch_authentic_source_bars(sym, start_date, end_date)
                if bars:
                    db_objects = [PriceDB(
                        symbol=b["symbol"], date=b["date"], open=b["open"], high=b["high"],
                        low=b["low"], close=b["close"], volume=b["volume"], source=b["source"]
                    ) for b in bars]
                    session.bulk_save_objects(db_objects)
                    session.commit()

    print("[SUCCESS] Authentic Nifty 500 backfill completed successfully!")

if __name__ == "__main__":
    run_fast_nifty500_backfill()
