import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text
from backend.core.postgres import engine

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def validate():
    print("============================================================")
    print(" F&O MASTER DATA VALIDATION")
    print("============================================================")

    try:
        with engine.connect() as conn:
            # 1. Check Futures
            res = conn.execute(text("SELECT count(*) FROM instruments WHERE segment = 'FUTURES'"))
            fut_count = res.scalar()

            # 2. Check Options
            res = conn.execute(text("SELECT count(*) FROM instruments WHERE segment = 'OPTIONS'"))
            opt_count = res.scalar()

            # 3. Verify Required Fields for existing instruments
            res = conn.execute(text("SELECT count(*) FROM instruments WHERE (underlying_symbol IS NULL OR expiry IS NULL)"))
            incomplete = res.scalar()

            print(f"FUTURES COUNT: {fut_count}")
            print(f"OPTIONS COUNT: {opt_count}")
            print(f"INCOMPLETE RECORDS: {incomplete}")

            status = "PASS" if (fut_count + opt_count) > 0 and incomplete == 0 else "FAIL"
            print(f"\nSTATUS: {status}")

            if status == "FAIL":
                sys.exit(1)
            else:
                sys.exit(0)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate()
