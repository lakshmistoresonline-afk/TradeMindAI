import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def fix():
    print("--- TRADEMIND AI: FINAL NUMERIC SCHEMA FIX ---")
    with engine.connect() as conn:
        print("[*] Fixing trigger_price in live_signals...")
        conn.execute(text("ALTER TABLE live_signals ALTER COLUMN trigger_price TYPE DOUBLE PRECISION USING trigger_price::text::double precision"))

        print("[*] Fixing trigger_condition in live_signals...")
        conn.execute(text("ALTER TABLE live_signals ALTER COLUMN trigger_condition TYPE VARCHAR USING trigger_condition::text"))

        conn.commit()
    print("Fix complete.")

if __name__ == "__main__":
    fix()
