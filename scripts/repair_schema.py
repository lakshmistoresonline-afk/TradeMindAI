import os
import sys
import sqlite3
from sqlalchemy import inspect

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.postgres import engine, StockDB, DATABASE_URL

def repair():
    if "sqlite" not in DATABASE_URL:
        print("Manual schema repair only supported for SQLite.")
        return

    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(stocks)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    # Get target columns from model
    mapper = inspect(StockDB)
    for column in mapper.attrs:
        col_name = column.key
        if col_name not in existing_cols:
            print(f"Adding missing column: {col_name}")
            # Simplified type mapping for SQLite
            col_type = "TEXT" # JSON or String
            if "Float" in str(column.expression.type):
                col_type = "REAL"
            elif "BigInteger" in str(column.expression.type) or "Integer" in str(column.expression.type):
                col_type = "INTEGER"

            try:
                cursor.execute(f"ALTER TABLE stocks ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Failed to add {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Schema repair complete.")

if __name__ == "__main__":
    repair()
