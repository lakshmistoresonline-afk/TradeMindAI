import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def fix():
    with engine.connect() as conn:
        print("--- FIXING CIPLA ---")
        # Get current entry
        res = conn.execute(text("SELECT entry_price, current_price FROM live_signals WHERE symbol = 'CIPLA'"))
        row = res.fetchone()
        if not row:
            print("CIPLA not found in live_signals.")
            return

        print(f"Before: Entry {row[0]} | Current {row[1]}")

        # Update current_price only
        new_price = 1358.0
        conn.execute(text(f"UPDATE live_signals SET current_price = {new_price}, current_price_timestamp = NOW() WHERE symbol = 'CIPLA'"))
        conn.commit()

        # Verify
        res = conn.execute(text("SELECT entry_price, current_price FROM live_signals WHERE symbol = 'CIPLA'"))
        row = res.fetchone()
        print(f"After:  Entry {row[0]} | Current {row[1]}")

if __name__ == "__main__":
    fix()
