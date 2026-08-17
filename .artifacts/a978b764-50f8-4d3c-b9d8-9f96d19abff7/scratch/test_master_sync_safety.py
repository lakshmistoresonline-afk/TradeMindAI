import os
import sys
import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
import importlib.util

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

# Import the populate function dynamically
spec = importlib.util.spec_from_file_location("populate_stocks_master", "terminal_master_scripts/02_populate_stocks_master.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
populate = module.populate

async def test_safety():
    print("============================================================")
    print(" REGRESSION TEST: STOCK MASTER SYNC SAFETY")
    print("============================================================")

    # 1. Record baseline
    with engine.connect() as conn:
        before_count = conn.execute(text("SELECT count(*) FROM historical_prices")).scalar()
        before_symbols = conn.execute(text("SELECT count(DISTINCT symbol) FROM historical_prices")).scalar()

    print(f"[*] Baseline: {before_count} rows, {before_symbols} symbols.")

    if before_count == 0:
        print("[!] SKIP: No historical data to protect. Run sync first.")
        return

    # 2. Run Sync
    print("[*] Running Stock Master Sync...")
    try:
        await populate()
    except SystemExit as e:
        if e.code != 0:
            print(f"[FAIL] Sync script exited with code {e.code}")
            sys.exit(1)

    # 3. Verify
    with engine.connect() as conn:
        after_count = conn.execute(text("SELECT count(*) FROM historical_prices")).scalar()
        after_symbols = conn.execute(text("SELECT count(DISTINCT symbol) FROM historical_prices")).scalar()

    print(f"[*] Post-Sync: {after_count} rows, {after_symbols} symbols.")

    if after_count < before_count:
        print(f"[FAIL] Data deletion detected! {before_count} -> {after_count}")
        sys.exit(1)

    if after_symbols < before_symbols:
        print(f"[FAIL] Symbol regression detected! {before_symbols} -> {after_symbols}")
        sys.exit(1)

    print("[PASS] Historical data preserved.")

if __name__ == "__main__":
    asyncio.run(test_safety())
