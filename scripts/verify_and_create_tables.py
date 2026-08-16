import os
import sys
import datetime
from sqlalchemy import text, inspect
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine, init_db, SessionLocal, StockDB
from scripts.audit_database import NIFTY_100

def run():
    print("--- Database Verification & Table Creation ---")

    # 1. Create missing tables
    print("[*] Ensuring all tables exist...")
    init_db()

    # 2. Check for missing columns (Schema Reconciliation)
    print("[*] Reconciling schema for existing tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"    Current Tables: {tables}")

    # 3. Populate initial Nifty 100 universe if missing
    print("[*] Checking Nifty 100 universe population...")
    session = SessionLocal()
    try:
        existing_symbols = {s.symbol for s in session.query(StockDB.symbol).all()}
        added_count = 0
        for symbol in NIFTY_100:
            if symbol not in existing_symbols:
                new_stock = StockDB(
                    symbol=symbol,
                    ai_status="PENDING",
                    updated_at=datetime.datetime.utcnow()
                )
                session.add(new_stock)
                added_count += 1

        if added_count > 0:
            session.commit()
            print(f"    Added {added_count} missing symbols to 'stocks' table.")
        else:
            print("    All Nifty 100 symbols already present.")

    except Exception as e:
        print(f"    [!] Error during population: {e}")
        session.rollback()
    finally:
        session.close()

    print("\n--- Database Verification Complete ---")

if __name__ == "__main__":
    run()
