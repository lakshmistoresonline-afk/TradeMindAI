"""
================================================================================
TradeMindAI: Fast Parallel Batch Backfill for All 500 Nifty Equities
================================================================================
Downloads 10-year daily authentic OHLCV bars in parallel batches using yfinance
and populates historical_prices in backend/local_operational.db.
================================================================================
"""

import sqlite3
import os
import datetime
import logging
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = r"D:\TradeMindAI\backend\local_operational.db"

# Ticker mapping overrides for non-standard symbol strings in stocks table
SYMBOL_MAP = {
    "BAJAJ_HLDNG": "BAJAJHLDNG",
    "Azad Engineering": "AZAD",
    "ACTIONCONE": "ACTIONIND",
    "BOROSWITCH": "BORORENEW",
    "CIE": "CIEINDIA",
    "CENTURYTEX": "CENTURYTEX",
    "GREENPANEL": "GREENPANEL",
    "GREENPLY": "GREENPLY",
    "GREENPOWER": "JPPOWER"
}

def fast_batch_backfill():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT symbol FROM stocks WHERE symbol IS NOT NULL AND trim(symbol) != '';")
    raw_symbols = [r[0].strip() for r in cursor.fetchall()]
    logger.info(f"=== Starting Fast Parallel Batch Backfill for {len(raw_symbols)} Stocks ===")

    # Prepare ticker strings
    ticker_map = {}
    for sym in raw_symbols:
        clean_sym = SYMBOL_MAP.get(sym, sym.replace("_", ""))
        ticker_str = f"{clean_sym}.NS"
        ticker_map[ticker_str] = sym

    tickers = list(ticker_map.keys())
    logger.info(f"[1/3] Downloading 10-year OHLCV data in parallel batches for {len(tickers)} tickers...")

    start_date = "2015-01-01"
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Download in batches of 50 tickers for stability
    batch_size = 50
    total_inserted = 0

    for i in range(0, len(tickers), batch_size):
        batch_tickers = tickers[i:i + batch_size]
        logger.info(f"Downloading batch {i//batch_size + 1}/{(len(tickers) + batch_size - 1)//batch_size} ({len(batch_tickers)} tickers)...")

        try:
            df = yf.download(
                batch_tickers,
                start=start_date,
                end=end_date,
                group_by="ticker",
                progress=False,
                auto_adjust=True,
                threads=True
            )

            if df.empty:
                continue

            rows_to_insert = []
            for ticker_str in batch_tickers:
                orig_sym = ticker_map[ticker_str]

                # Extract ticker dataframe
                if len(batch_tickers) == 1:
                    ticker_df = df
                else:
                    if ticker_str in df.columns.levels[0]:
                        ticker_df = df[ticker_str]
                    else:
                        continue

                if ticker_df.empty:
                    continue

                # Get existing dates in DB for symbol
                cursor.execute("SELECT strftime('%Y-%m-%d', date) FROM historical_prices WHERE symbol = ?;", (orig_sym,))
                existing_dates = {r[0] for r in cursor.fetchall()}

                for idx_dt, row in ticker_df.dropna(how="all").iterrows():
                    try:
                        c_open = float(row.get("Open", 0))
                        c_high = float(row.get("High", 0))
                        c_low = float(row.get("Low", 0))
                        c_close = float(row.get("Close", 0))
                        c_vol = float(row.get("Volume", 0))

                        if c_open > 0 and c_high > 0 and c_low > 0 and c_close > 0 and c_high >= c_low:
                            d_str = idx_dt.strftime("%Y-%m-%d")
                            if d_str not in existing_dates:
                                rows_to_insert.append((
                                    orig_sym,
                                    idx_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                    c_open,
                                    c_high,
                                    c_low,
                                    c_close,
                                    max(0.0, c_vol),
                                    0,
                                    "YFINANCE_AUTHENTIC"
                                ))
                                existing_dates.add(d_str)
                    except Exception:
                        continue

            if rows_to_insert:
                cursor.executemany("""
                    INSERT INTO historical_prices (symbol, date, open, high, low, close, volume, open_interest, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, rows_to_insert)
                conn.commit()
                total_inserted += len(rows_to_insert)
                logger.info(f"  Inserted {len(rows_to_insert):,} authentic bars for batch.")

        except Exception as e:
            logger.error(f"Error processing batch {i}: {e}")

    # Deduplicate DB
    cursor.execute("""
        DELETE FROM historical_prices
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM historical_prices
            GROUP BY symbol, strftime('%Y-%m-%d', date)
        );
    """)
    conn.commit()

    conn.close()
    logger.info(f"=== Fast Parallel Batch Backfill Complete: Inserted {total_inserted:,} authentic bars ===")

if __name__ == "__main__":
    fast_batch_backfill()
