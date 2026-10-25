"""
================================================================================
TradeMindAI: Authentic Nifty 500 Market Price Backfill Script
================================================================================
Fetches 10-year authentic daily OHLCV bars from Yahoo Finance for all canonical
Nifty 500 stock symbols in stocks table.
Saves validated bars to historical_prices in backend/local_operational.db.
================================================================================
"""

import os
import sys
import datetime
import logging
import sqlite3
import pandas as pd

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.services.historical_backfill_service import HistoricalBackfillService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = r"D:\TradeMindAI\backend\local_operational.db"

def backfill_authentic_prices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT symbol FROM stocks WHERE symbol IS NOT NULL AND trim(symbol) != '';")
    stocks = [r[0].strip() for r in cursor.fetchall()]
    logger.info(f"=== Starting Authentic Market Data Backfill for {len(stocks)} Equities ===")

    start_dt = datetime.datetime(2015, 1, 1)
    end_dt = datetime.datetime.now()

    inserted_total = 0
    symbols_processed = 0

    for idx, sym in enumerate(stocks, 1):
        # Check existing bar count for symbol
        cursor.execute("SELECT COUNT(*) FROM historical_prices WHERE symbol = ?;", (sym,))
        existing_count = cursor.fetchone()[0]

        if existing_count >= 1500:
            logger.info(f"[{idx}/{len(stocks)}] {sym:<15}: Already has {existing_count} authentic bars. Skipping.")
            symbols_processed += 1
            continue

        logger.info(f"[{idx}/{len(stocks)}] {sym:<15}: Fetching authentic bars from Yahoo Finance...")
        bars = HistoricalBackfillService.fetch_authentic_source_bars(sym, start_dt, end_dt)

        if not bars:
            logger.warning(f"[{idx}/{len(stocks)}] {sym:<15}: No authentic bars returned.")
            continue

        # Get existing dates for deduplication
        cursor.execute("SELECT strftime('%Y-%m-%d', date) FROM historical_prices WHERE symbol = ?;", (sym,))
        existing_dates = {r[0] for r in cursor.fetchall()}

        new_rows = []
        for b in bars:
            d_str = pd.to_datetime(b["date"]).strftime("%Y-%m-%d")
            if d_str not in existing_dates:
                new_rows.append((
                    b["symbol"],
                    pd.to_datetime(b["date"]).strftime("%Y-%m-%d %H:%M:%S"),
                    b["open"],
                    b["high"],
                    b["low"],
                    b["close"],
                    b["volume"],
                    0,  # open_interest
                    "YFINANCE_AUTHENTIC"
                ))

        if new_rows:
            cursor.executemany("""
                INSERT INTO historical_prices (symbol, date, open, high, low, close, volume, open_interest, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, new_rows)
            conn.commit()
            inserted_total += len(new_rows)
            logger.info(f"[{idx}/{len(stocks)}] {sym:<15}: Inserted {len(new_rows)} authentic bars.")
        else:
            logger.info(f"[{idx}/{len(stocks)}] {sym:<15}: All fetched bars already present.")

        symbols_processed += 1

    conn.close()
    logger.info(f"=== Backfill Complete: Inserted {inserted_total:,} authentic bars across {symbols_processed} equities ===")

if __name__ == "__main__":
    backfill_authentic_prices()
