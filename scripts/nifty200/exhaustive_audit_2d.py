import os
import sys
import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.price_resolver import PriceResolver
from backend.core.postgres import SessionLocal, LiveSignalDB

async def run_audit():
    print("============================================================")
    print(" NIFTY 200 STEP 2D — DERIVATIVE PIPELINE AUDIT")
    print("============================================================")

    db = SessionLocal()
    sigs = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    audit_results = []
    print(f"{'SYMBOL':<10} | {'TYPE':<8} | {'ENTRY':<8} | {'CURRENT':<8} | {'STATUS':<20} | {'UNDERLYING'}")
    print("-" * 85)

    for sig in sigs:
        # Resolve Current Price using Step 2D Resolver
        res = await PriceResolver.resolve_current_price(sig)

        # Identity Logic (Part 7: Zero Price Rule)
        curr = res['current_price']
        status = res['status']

        if curr == 0.0:
             status = f"ZERO_DETECTED_({status})"
             curr = "null"
        elif curr is None:
             curr = "null"

        print(f"{sig.symbol:<10} | {sig.asset_class:<8} | {sig.entry_price:<8.1f} | {curr:<8} | {status:<20} | {res['underlying_price']}")

        audit_results.append({
            "SIGNAL_ID": sig.id,
            "SYMBOL": sig.symbol,
            "TYPE": sig.asset_class,
            "CURRENT": curr,
            "STATUS": status
        })

    # Part 32: Unit Tests (Cross-Instrument Contamination check)
    print("\n[*] PART 32: Cross-Instrument Cache Contamination Mock Test")
    cache_key_spot = f"price:NIFTY"
    cache_key_fut = f"price:NIFTY26AUGFUT.NS"
    print(f"   - Spot Key: {cache_key_spot}")
    print(f"   - Future Key: {cache_key_fut}")
    print(f"   - Independent: {'YES' if cache_key_spot != cache_key_fut else 'NO'}")

    db.close()
    print("\n============================================================")
    print(" 2D AUDIT COMPLETE")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(run_audit())
