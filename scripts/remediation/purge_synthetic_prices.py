"""
================================================================================
TradeMindAI: Operational Database Price Table Remediation Script
================================================================================
Purges all legacy synthetic sine-wave price records ('NIFTY500_BULK_2015' and
'BACKFILL_2015_CANONICAL') from historical_prices in backend/local_operational.db.
Strips leading/trailing whitespace from stock symbols in stocks table.
================================================================================
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = r"D:\TradeMindAI\backend\local_operational.db"

def remediate_database():
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    logger.info("=== Starting Operational Database Remediation ===")

    # 1. Clean stock symbols whitespace in stocks table
    cursor.execute("SELECT symbol FROM stocks;")
    stocks = cursor.fetchall()
    cleaned_count = 0
    for (sym,) in stocks:
        clean_sym = sym.strip()
        if clean_sym != sym:
            cursor.execute("UPDATE stocks SET symbol = ? WHERE symbol = ?;", (clean_sym, sym))
            cursor.execute("UPDATE historical_prices SET symbol = ? WHERE symbol = ?;", (clean_sym, sym))
            cleaned_count += 1
    logger.info(f"[1/3] Cleaned whitespace for {cleaned_count} stock symbols.")

    # 2. Delete synthetic sine-wave rows from historical_prices
    cursor.execute("SELECT COUNT(*) FROM historical_prices WHERE source IN ('NIFTY500_BULK_2015', 'BACKFILL_2015_CANONICAL');")
    synthetic_count = cursor.fetchone()[0]
    logger.info(f"[2/3] Found {synthetic_count:,} synthetic/unverified price rows to purge...")

    cursor.execute("DELETE FROM historical_prices WHERE source IN ('NIFTY500_BULK_2015', 'BACKFILL_2015_CANONICAL');")
    purged_count = cursor.rowcount
    conn.commit()
    logger.info(f"[2/3] Successfully purged {purged_count:,} synthetic rows from historical_prices.")

    # 3. Deduplicate historical_prices by (symbol, date)
    cursor.execute("""
        DELETE FROM historical_prices
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM historical_prices
            GROUP BY symbol, strftime('%Y-%m-%d', date)
        );
    """)
    dedup_count = cursor.rowcount
    conn.commit()
    logger.info(f"[3/3] Deduplicated {dedup_count:,} duplicate price rows in historical_prices.")

    # Final Verification Summary
    cursor.execute("SELECT source, COUNT(*) FROM historical_prices GROUP BY source;")
    sources = cursor.fetchall()
    logger.info("=== Post-Remediation historical_prices Source Summary ===")
    for src, cnt in sources:
        logger.info(f"  Source: {src!r:<30} Count: {cnt:,}")

    cursor.execute("SELECT COUNT(*), COUNT(DISTINCT symbol) FROM historical_prices;")
    total_rows, total_syms = cursor.fetchone()
    logger.info(f"Total Authentic Rows Remaining: {total_rows:,} across {total_syms} symbols.")

    conn.close()

if __name__ == "__main__":
    remediate_database()
