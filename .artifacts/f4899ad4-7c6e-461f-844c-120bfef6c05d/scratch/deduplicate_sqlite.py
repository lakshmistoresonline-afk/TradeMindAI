
import sqlite3
import os

def deduplicate():
    db_path = "backend/local_operational.db"
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- DEDUPLICATING HISTORICAL_PRICES ---")

    # Identify duplicates
    cursor.execute("""
        SELECT symbol, date, count(*)
        FROM historical_prices
        GROUP BY symbol, date
        HAVING count(*) > 1
    """)
    duplicates = cursor.fetchall()
    print(f"Found {len(duplicates)} symbol/date pairs with duplicates.")

    if not duplicates:
        conn.close()
        return

    # Create temporary table to store one of each
    cursor.execute("DROP TABLE IF EXISTS historical_prices_temp")
    cursor.execute("CREATE TABLE historical_prices_temp AS SELECT * FROM historical_prices WHERE 1=0")

    # Insert unique rows into temp
    cursor.execute("""
        INSERT INTO historical_prices_temp
        SELECT * FROM historical_prices
        GROUP BY symbol, date
    """)

    unique_count = cursor.execute("SELECT count(*) FROM historical_prices_temp").fetchone()[0]
    old_count = cursor.execute("SELECT count(*) FROM historical_prices").fetchone()[0]

    print(f"Old count: {old_count}")
    print(f"New count: {unique_count}")
    print(f"Removed: {old_count - unique_count} duplicate rows.")

    # Replace old table
    cursor.execute("DROP TABLE historical_prices")
    cursor.execute("ALTER TABLE historical_prices_temp RENAME TO historical_prices")

    # Re-create indexes
    cursor.execute("CREATE INDEX idx_historical_prices_symbol ON historical_prices(symbol)")
    cursor.execute("CREATE INDEX idx_historical_prices_date ON historical_prices(date)")

    conn.commit()
    conn.close()
    print("Deduplication complete.")

if __name__ == "__main__":
    deduplicate()
