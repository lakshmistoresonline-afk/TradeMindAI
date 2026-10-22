"""
================================================================================
TradeMindAI: Canonical Nifty 500 Data Reconciliation & Authentic Backfill Script
================================================================================
1. Resolves duplicate observation conflicts in PriceDB across all 500 constituents
   by deterministically retaining the canonical provider source row per (symbol, date).
2. Backfills authentic market price history from yfinance for missing/no-data symbols.
================================================================================
"""

import os
import sys
import datetime
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import create_engine, text

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB, StockDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS, get_nifty_500_universe, validate_nifty500_universe
from backend.services.historical_backfill_service import HistoricalBackfillService

def reconcile_duplicate_conflicts_and_backfill():
    print("================================================================================")
    print("  TRADEMIND AI: NIFTY 500 RECONCILIATION & AUTHENTIC MARKET DATA BACKFILL")
    print("================================================================================\n")

    validate_nifty500_universe(NIFTY_500_SYMBOLS)
    symbols = NIFTY_500_SYMBOLS
    print(f"[*] Validated canonical Nifty 500 universe size: {len(symbols)} stocks.")

    start_date = datetime(2015, 1, 1)
    end_date = datetime(2026, 10, 17)

    source_priority = {
        "YFINANCE_AUTHENTIC": 100,
        "YFinance_5Y_Canonical": 80,
        "YFinance_10Y_Canonical": 70,
        "BACKFILL_2015_CANONICAL": 50,
        "NIFTY500_BULK_2015": 30,
        "NIFTY500_FULL_SYNC_2015": 20,
    }

    total_deleted = 0
    total_added = 0

    with SessionLocal() as session:
        print("[*] Phase 1: Reconciling duplicate observation conflicts in PriceDB...")

        # Process in chunks of symbols for memory safety
        chunk_size = 25
        for idx in range(0, len(symbols), chunk_size):
            chunk_syms = symbols[idx:idx+chunk_size]
            for sym in chunk_syms:
                bars = session.query(PriceDB).filter(PriceDB.symbol == sym).order_by(PriceDB.date.asc()).all()
                if not bars:
                    continue

                bars_by_date = {}
                for b in bars:
                    if b.date not in bars_by_date:
                        bars_by_date[b.date] = []
                    bars_by_date[b.date].append(b)

                ids_to_delete = []
                for dt, group in bars_by_date.items():
                    if len(group) > 1:
                        # Sort by source priority descending, then by id descending
                        sorted_group = sorted(
                            group,
                            key=lambda b: (source_priority.get(str(b.source).strip(), 10), b.id),
                            reverse=True
                        )
                        canonical_bar = sorted_group[0]
                        for dup in sorted_group[1:]:
                            ids_to_delete.append(dup.id)

                if ids_to_delete:
                    # Delete duplicate row IDs in sub-chunks
                    for i in range(0, len(ids_to_delete), 500):
                        sub_ids = ids_to_delete[i:i+500]
                        session.query(PriceDB).filter(PriceDB.id.in_(sub_ids)).delete(synchronize_session=False)
                    session.commit()
                    total_deleted += len(ids_to_delete)

            print(f"    [+] Processed duplicate reconciliation chunk {idx // chunk_size + 1}/{(len(symbols) + chunk_size - 1) // chunk_size}...")

        print(f"[SUCCESS] Phase 1 complete. Deleted {total_deleted} duplicate conflict rows.")

        print("\n[*] Phase 2: Backfilling authentic market data for no-data / missing symbols...")
        for idx, sym in enumerate(symbols, 1):
            existing_cnt = session.query(PriceDB.date).filter(PriceDB.symbol == sym).count()
            if existing_cnt < 200:
                print(f"    [+] Fetching authentic market history for {sym} (current bars: {existing_cnt})...")
                bars = HistoricalBackfillService.fetch_authentic_source_bars(sym, start_date, end_date)
                if bars:
                    # Filter out dates that already exist
                    existing_dts = {p[0] for p in session.query(PriceDB.date).filter(PriceDB.symbol == sym).all()}
                    new_bars = [b for b in bars if b["date"] not in existing_dts]

                    if new_bars:
                        db_objects = [PriceDB(
                            symbol=b["symbol"], date=b["date"], open=b["open"], high=b["high"],
                            low=b["low"], close=b["close"], volume=b["volume"], source=b["source"]
                        ) for b in new_bars]
                        session.bulk_save_objects(db_objects)
                        session.commit()
                        total_added += len(db_objects)
                        print(f"        -> Inserted {len(db_objects)} authentic price bars for {sym}.")

    print(f"\n[SUCCESS] Reconciled and backfilled PriceDB completely!")
    print(f"          Total duplicate rows deleted : {total_deleted}")
    print(f"          Total authentic bars added   : {total_added}")

if __name__ == "__main__":
    reconcile_duplicate_conflicts_and_backfill()
