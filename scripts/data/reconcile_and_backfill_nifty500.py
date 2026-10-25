"""
================================================================================
TradeMindAI: Canonical Nifty 500 Data Reconciliation & Authentic Backfill Script
================================================================================
Fail-Closed Preservation Policy:
- Never automatically delete or overwrite existing observation rows.
- Detect and report duplicate conflicts without destructive deletion.
- Backfill authentic market price history from yfinance for missing/no-data symbols.
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

    total_conflicts_detected = 0
    total_added = 0

    with SessionLocal() as session:
        print("[*] Phase 1: Detecting duplicate observation conflicts in PriceDB (Preservation Mode)...")

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

                for dt, group in bars_by_date.items():
                    if len(group) > 1:
                        total_conflicts_detected += len(group) - 1

            print(f"    [+] Audited duplicate conflict chunk {idx // chunk_size + 1}/{(len(symbols) + chunk_size - 1) // chunk_size} (Conflicts logged: {total_conflicts_detected})...")

        print(f"[SUCCESS] Phase 1 complete. Detected {total_conflicts_detected} duplicate conflict rows (Preserved without deletion).")

        print("\n[*] Phase 2: Backfilling authentic market data for no-data / missing symbols...")
        for idx, sym in enumerate(symbols, 1):
            existing_cnt = session.query(PriceDB.date).filter(PriceDB.symbol == sym).count()
            if existing_cnt < 200:
                print(f"    [+] Fetching authentic market history for {sym} (current bars: {existing_cnt})...")
                bars = HistoricalBackfillService.fetch_authentic_source_bars(sym, start_date, end_date)
                if bars:
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

    print(f"\n[SUCCESS] Reconciled and backfilled PriceDB completely (Fail-Closed Preservation Mode)!")
    print(f"          Total duplicate conflicts logged : {total_conflicts_detected}")
    print(f"          Total authentic bars added       : {total_added}")

if __name__ == "__main__":
    reconcile_duplicate_conflicts_and_backfill()
