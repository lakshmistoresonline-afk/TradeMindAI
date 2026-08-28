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
    print("--- TRADEMIND AI: FIXING LIFECYCLE COLUMN TYPES ---")
    with engine.connect() as conn:
        try:
            print("[*] Altering validated_at to TIMESTAMP...")
            conn.execute(text("ALTER TABLE live_signals ALTER COLUMN validated_at TYPE TIMESTAMP USING validated_at::text::timestamp"))

            print("[*] Altering triggered_at to TIMESTAMP...")
            conn.execute(text("ALTER TABLE live_signals ALTER COLUMN triggered_at TYPE TIMESTAMP USING triggered_at::text::timestamp"))

            print("[*] Altering outcome_date to TIMESTAMP...")
            conn.execute(text("ALTER TABLE live_signals ALTER COLUMN outcome_date TYPE TIMESTAMP USING outcome_date::text::timestamp"))

            conn.commit()
            print("[+] Columns successfully converted to TIMESTAMP.")
        except Exception as e:
            print(f"[!] Conversion failed: {e}")
            print("[*] Attempting a safer drop and recreate if columns are empty...")
            try:
                conn.execute(text("ALTER TABLE live_signals DROP COLUMN validated_at"))
                conn.execute(text("ALTER TABLE live_signals DROP COLUMN triggered_at"))
                conn.execute(text("ALTER TABLE live_signals ADD COLUMN validated_at TIMESTAMP"))
                conn.execute(text("ALTER TABLE live_signals ADD COLUMN triggered_at TIMESTAMP"))
                conn.commit()
                print("[+] Recreated columns successfully.")
            except Exception as e2:
                print(f"[!] Recreate failed: {e2}")

if __name__ == "__main__":
    fix()
