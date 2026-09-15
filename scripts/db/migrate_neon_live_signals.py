import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv('backend/.env')

db_url = os.getenv("POSTGRES_URL")
if not db_url:
    print("No POSTGRES_URL found in env")
    exit(1)

print(f"Connecting to: {db_url[:50]}...")
engine = sqlalchemy.create_engine(db_url)
try:
    with engine.connect() as conn:
        print("[*] Ensuring quality_class exists in live_signals...")
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS quality_class VARCHAR"))

        print("[*] Ensuring quality_class exists in shadow_signals...")
        conn.execute(text("ALTER TABLE shadow_signals ADD COLUMN IF NOT EXISTS quality_class VARCHAR"))

        conn.commit()
        print("[+] Migrations successful.")
except Exception as e:
    print(f"Error: {e}")
finally:
    engine.dispose()
