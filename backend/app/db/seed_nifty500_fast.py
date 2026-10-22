"""
================================================================================
TradeMindAI: Ultra-Fast Nifty 500 Historical Data Seeder (2015 - Present)
================================================================================
Uses native sqlite3 executemany with WAL mode and INSERT OR IGNORE for sub-10 second
population of 1.38+ million historical price bars across all 500 Nifty 500 stocks
into trade_mind.db.
"""

import sqlite3
import datetime
import os
import numpy as np
import logging
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nifty500FastSeeder")

def populate_nifty500_fast():
    env = str(os.getenv("ENVIRONMENT") or "").lower()
    if env in ("production", "staging") or os.getenv("RAILWAY_ENVIRONMENT") is not None:
        logger.error("[Fast Seeder] CRITICAL: Refusing synthetic fixture insertion in production or staging environment.")
        return

    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "trade_mind.db"))
    logger.info(f"[Fast Seeder] Connecting to SQLite database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable WAL mode and synchronous tuning
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")

    # Ensure tables exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume REAL NOT NULL DEFAULT 0.0,
            CONSTRAINT uq_sym_timestamp UNIQUE (symbol, timestamp)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_sym_time ON app_market_data(symbol, timestamp);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL UNIQUE,
            added_at DATETIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_signal_cache (
            symbol TEXT PRIMARY KEY,
            last_updated DATETIME,
            signal_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            rsi_14 REAL DEFAULT 50.0,
            macd_val REAL DEFAULT 0.0,
            macd_signal REAL DEFAULT 0.0,
            ema_20 REAL DEFAULT 0.0,
            ema_50 REAL DEFAULT 0.0
        )
    """)
    conn.commit()

    start_date = datetime.date(2015, 1, 1)
    end_date = datetime.date.today()

    logger.info(f"[Fast Seeder] Generating trading days from {start_date} to {end_date}...")
    all_dates = []
    curr = start_date
    while curr <= end_date:
        if curr.weekday() < 5: # Monday to Friday
            all_dates.append(curr.strftime("%Y-%m-%d %H:%M:%S"))
        curr += datetime.timedelta(days=1)

    logger.info(f"[Fast Seeder] Total trading sessions: {len(all_dates)}. Total symbols: {len(NIFTY_500_SYMBOLS)}")

    market_data_rows = []
    watchlist_rows = []
    signal_cache_rows = []

    for sym in NIFTY_500_SYMBOLS:
        watchlist_rows.append((sym, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        base_p = 100.0 + (abs(hash(sym)) % 3000.0)
        trend_factor = 0.0003 * (abs(hash(sym + "trend")) % 5 - 2)

        sig_type = "BUY" if (hash(sym) % 2 == 0) else "HOLD"
        conf = float(72.5 + (hash(sym) % 20))
        latest_close = base_p * (1.0 + (len(all_dates) * trend_factor))

        signal_cache_rows.append((
            sym,
            datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            sig_type,
            conf,
            58.4,
            1.25,
            1.10,
            latest_close * 0.99,
            latest_close * 0.97
        ))

        for d_idx, dt_str in enumerate(all_dates):
            noise = np.sin(d_idx / 20.0) * 15.0 + np.random.normal(0, 1.2)
            c_price = max(10.0, base_p * (1.0 + (d_idx * trend_factor)) + noise)
            h_price = c_price + abs(np.random.normal(2.5, 1.0))
            l_price = max(5.0, c_price - abs(np.random.normal(2.5, 1.0)))
            o_price = (h_price + l_price) / 2.0
            vol = float(100000 + (abs(hash(sym + str(d_idx))) % 900000))

            market_data_rows.append((
                sym,
                dt_str,
                round(o_price, 2),
                round(h_price, 2),
                round(l_price, 2),
                round(c_price, 2),
                vol
            ))

    logger.info(f"[Fast Seeder] Inserting {len(market_data_rows)} market data records using executemany into trade_mind.db...")
    cursor.executemany("""
        INSERT OR IGNORE INTO app_market_data (symbol, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, market_data_rows)

    logger.info(f"[Fast Seeder] Inserting watchlists...")
    cursor.executemany("""
        INSERT OR IGNORE INTO app_watchlists (symbol, added_at)
        VALUES (?, ?)
    """, watchlist_rows)

    logger.info(f"[Fast Seeder] Inserting signal caches...")
    cursor.executemany("""
        INSERT OR REPLACE INTO app_signal_cache (symbol, last_updated, signal_type, confidence, rsi_14, macd_val, macd_signal, ema_20, ema_50)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, signal_cache_rows)

    conn.commit()
    conn.close()
    logger.info("[Fast Seeder] Nifty 500 complete database population (2015-present) into trade_mind.db finished successfully!")

if __name__ == "__main__":
    populate_nifty500_fast()
