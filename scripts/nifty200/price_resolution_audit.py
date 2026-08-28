import os
import sys
import asyncio
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.price_resolver import PriceResolver
from backend.core.postgres import SessionLocal, LiveSignalDB

async def audit():
    print("============================================================")
    print(" NIFTY 200 STEP 2C — CANONICAL PRICE RESOLUTION AUDIT")
    print("============================================================")

    db = SessionLocal()
    sigs = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    print(f"[*] Auditing {len(sigs)} baseline signals...")
    print(f"{'SYMBOL':<12} | {'TYPE':<8} | {'ENTRY':<8} | {'CURRENT':<8} | {'UNDERLYING':<10} | {'STATUS'}")
    print("-" * 75)

    audit_results = []
    for s in sigs:
        # Resolve using Step 2C Logic
        res = await PriceResolver.resolve_current_price(s)

        # Update Database
        s.current_price = res["current_price"]
        s.underlying_price = res["underlying_price"]
        s.normalized_current_price = res["normalized_current_price"]
        s.current_price_timestamp = res["timestamp"]
        s.price_source = res["source"]

        # Identity Validation
        mapping_valid = True
        if s.asset_class in ["OPTIONS", "FUTURES"]:
            # Part 10: Derivative Test
            if abs(s.current_price - s.underlying_price) < 0.01:
                # Same price as spot is a failure in mapping
                mapping_valid = False

        status_str = res["status"]
        if not mapping_valid: status_str = "MAPPING_FAILURE"

        print(f"{s.symbol:<12} | {s.asset_class:<8} | {s.entry_price:<8.1f} | {s.current_price:<8.2f} | {s.underlying_price:<10.1f} | {status_str}")

        audit_results.append({
            "ID": s.id,
            "SYMBOL": s.symbol,
            "TYPE": s.asset_class,
            "ENTRY": s.entry_price,
            "CURRENT": s.current_price,
            "UNDERLYING": s.underlying_price,
            "STATUS": status_str
        })

    db.commit()
    db.close()

    # Summary
    failures = [r for r in audit_results if r["STATUS"] in ["MAPPING_FAILURE", "ERROR", "INSTRUMENT_NOT_FOUND"]]
    print("\n" + "=" * 60)
    if not failures:
        print(" [SUCCESS] All signals passed Canonical Price Resolution.")
    else:
        print(f" [!] Audit Failed with {len(failures)} resolution errors.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(audit())
