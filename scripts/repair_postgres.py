import os
import sys
from sqlalchemy import text, inspect
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine, Base

def repair():
    inspector = inspect(engine)
    with engine.connect() as conn:
        for table_name, model in Base.metadata.tables.items():
            print(f"[*] Auditing table: {table_name}")
            try:
                existing_cols = {col['name'] for col in inspector.get_columns(table_name)}
            except:
                print(f"    [!] Table {table_name} does not exist. Skipping (run init_db first).")
                continue

            for col_name, column in model.columns.items():
                if col_name not in existing_cols:
                    print(f"    [+] Adding missing column to {table_name}: {col_name}")

                    col_type = "JSON"
                    if "Float" in str(column.type):
                        col_type = "DOUBLE PRECISION"
                    elif "BigInteger" in str(column.type):
                        col_type = "BIGINT"
                    elif "Integer" in str(column.type):
                        col_type = "INTEGER"
                    elif "String" in str(column.type):
                        col_type = "VARCHAR"
                    elif "DateTime" in str(column.type):
                        col_type = "TIMESTAMP"

                    try:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                    except Exception as e:
                        print(f"    [!] Failed to add {col_name}: {e}")

    print("Postgres universal schema repair complete.")

if __name__ == "__main__":
    repair()
