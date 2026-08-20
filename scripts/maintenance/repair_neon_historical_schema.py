
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def repair():
    pg_url = os.getenv("POSTGRES_URL")
    if not pg_url:
        print("POSTGRES_URL not found")
        return

    engine = create_engine(pg_url)
    with engine.connect() as conn:
        print("--- REPAIRING NEON SCHEMA: historical_prices ---")

        # 1. source: json -> varchar
        try:
            print("[*] Converting source to VARCHAR...")
            # We use USING to handle existing data if any
            conn.execute(text("ALTER TABLE historical_prices ALTER COLUMN source TYPE VARCHAR(50) USING source::text"))
            print("[+] source converted.")
        except Exception as e:
            print(f"[-] Failed source: {e}")

        # 2. open_interest: json -> bigint
        try:
            print("[*] Converting open_interest to BIGINT...")
            conn.execute(text("ALTER TABLE historical_prices ALTER COLUMN open_interest TYPE BIGINT USING (open_interest::text)::bigint"))
            print("[+] open_interest converted.")
        except Exception as e:
            print(f"[-] Failed open_interest: {e}")

        # 3. indicators: text -> jsonb (Optional but recommended for performance/queries)
        try:
            print("[*] Converting indicators to JSONB...")
            conn.execute(text("ALTER TABLE historical_prices ALTER COLUMN indicators TYPE JSONB USING indicators::jsonb"))
            print("[+] indicators converted.")
        except Exception as e:
            print(f"[-] Failed indicators: {e}")

        conn.commit()
    print("Repair complete.")

if __name__ == "__main__":
    repair()
