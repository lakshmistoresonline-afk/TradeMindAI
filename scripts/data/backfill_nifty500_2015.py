"""
================================================================================
TradeMindAI: Complete Nifty 500 2015-to-Present Price Backfill Engine
================================================================================
1. Expands universe to include all 500 Nifty 500 stocks from nifty500_symbols.py.
2. Backfills authentic daily OHLCV market history from 2015-01-01 to present via provider adapter.
Synthetic price generation is strictly forbidden. Missing data remains missing.
Fail-Closed: BUY-only signal operation, zero live execution, REAL_TRADING=false.
================================================================================
"""

import os
import sys
import datetime
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, StockDB, PriceDB
from backend.app.db.nifty500_symbols import get_nifty_500_universe, validate_nifty500_universe
from backend.services.historical_backfill_service import HistoricalBackfillService

def run_nifty500_backfill():
    print("================================================================================")
    print("  TRADEMIND AI: AUTHENTIC NIFTY 500 2015-PRESENT PRICE BACKFILL ENGINE")
    print("================================================================================\n")

    universe_dict = get_nifty_500_universe()
    symbols = list(universe_dict.keys())
    validate_nifty500_universe(symbols)
    print(f"[*] Loaded Nifty 500 Universe: exactly {len(symbols)} authentic constituents.")

    start_date = datetime(2015, 1, 1)
    end_date = datetime(2026, 10, 17)

    added_stocks = 0
    added_prices = 0

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
                added_stocks += 1

        if new_stocks:
            session.bulk_save_objects(new_stocks)
            session.commit()
            print(f"   [+] Added {added_stocks} new Nifty 500 stocks to master registry.")

        all_stocks = session.query(StockDB).all()
        print(f"[*] Backfilling authentic price history from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} for {len(all_stocks)} stocks...")

        for idx, stock in enumerate(all_stocks, 1):
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
                    added_prices += len(db_objects)

            if idx % 50 == 0 or idx == len(all_stocks):
                print(f"   [+] Audited/Backfilled price history for {idx}/{len(all_stocks)} stocks...")

    print(f"[SUCCESS] Nifty 500 2015-Present Authentic Backfill complete. Total added prices: {added_prices}")
    return {"status": "SUCCESS", "stocks": len(symbols), "added_prices": added_prices}

if __name__ == "__main__":
    run_nifty500_backfill()
