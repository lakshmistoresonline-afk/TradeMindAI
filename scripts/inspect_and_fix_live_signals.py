import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def inspect_and_fix():
    print("--- TRADEMIND AI: INSPECTING LIVE_SIGNALS SCHEMA ---")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'live_signals'"))
        cols = res.fetchall()
        for c in cols:
            print(f"[*] Column: {c[0]} | Type: {c[1]}")
            if c[1].lower() == 'json' or c[1].lower() == 'jsonb':
                print(f"    [!] Converting {c[0]} to TEXT...")
                conn.execute(text(f"ALTER TABLE live_signals ALTER COLUMN {c[0]} TYPE TEXT USING {c[0]}::text"))

        conn.commit()
    print("Audit/Fix complete.")

if __name__ == "__main__":
    inspect_and_fix()
