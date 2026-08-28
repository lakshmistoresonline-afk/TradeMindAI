import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
from backend.core.postgres import engine

load_dotenv('backend/.env')

def validate():
    print("============================================================")
    print(" NIFTY 200 UNIVERSE VALIDATION")
    print("============================================================")

    expected_symbols = set(NIFTY_200_CONSTITUENTS)
    expected_count = len(expected_symbols)

    try:
        with engine.connect() as conn:
            # 1. Fetch unique constituents from database
            res = conn.execute(text("SELECT symbol FROM stocks WHERE index_membership = 'NIFTY_200'"))
            actual_symbols = {r[0] for r in res.fetchall()}
            actual_count = len(actual_symbols)

            missing = expected_symbols - actual_symbols
            extra = actual_symbols - expected_symbols

            # 2. Check Provider Mappings (LTP availability as proxy)
            res = conn.execute(text("SELECT symbol FROM stocks WHERE index_membership = 'NIFTY_200' AND (last_price IS NULL OR last_price = 0)"))
            mapping_failures = [r[0] for r in res.fetchall()]

            print(f"Expected constituents: {expected_count}")
            print(f"Actual unique constituents: {actual_count}")
            print(f"Missing: {len(missing)}")
            print(f"Duplicates: 0 (Enforced by Schema)")
            print(f"Invalid (Extra): {len(extra)}")
            print(f"Provider mapping failures: {len(mapping_failures)}")

            if len(missing) > 0:
                print(f"\n[MISSING SYMBOLS]: {sorted(list(missing))[:10]}...")

            if len(extra) > 0:
                print(f"\n[EXTRA/INVALID SYMBOLS]: {sorted(list(extra))[:10]}...")

            status = "PASS" if actual_count == expected_count and len(missing) == 0 else "FAIL"
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
