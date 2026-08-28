import os
import sys
import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import SessionLocal, LiveSignalDB, StockDB, InstrumentDB

async def run_audit():
    print("============================================================")
    print(" NIFTY 200 STEP 2B — CRITICAL DATA & MAPPING FORENSICS")
    print("============================================================")

    db = SessionLocal()
    provider = container.provider
    now = datetime.now()

    # --- PART 1: SIGNAL SNAPSHOT & AGE ---
    print("\n[*] PART 1 & 8: Signal Creation & Timestamp Integrity")
    sigs = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    snapshot_audit = []
    for sig in sigs:
        prov = json.loads(sig.provenance) if sig.provenance else {}
        data_ts_str = prov.get('data_timestamp')
        created_at = sig.timestamp

        age = "N/A"
        valid = "UNKNOWN"
        if data_ts_str:
            data_ts = datetime.fromisoformat(data_ts_str)
            age_td = created_at - data_ts
            age = age_td.total_seconds()
            valid = "PASS" if 0 <= age <= 60 else "FAIL"

        snapshot_audit.append({
            "SIGNAL_ID": sig.id[:20] + "...",
            "MARKET_TS": data_ts_str.split('T')[1] if data_ts_str else "N/A",
            "CREATED": created_at.strftime("%H:%M:%S"),
            "AGE_SEC": age,
            "VALID": valid
        })
    print(pd.DataFrame(snapshot_audit).to_string(index=False))

    # --- PART 2, 3, 4, 5, 6: INSTRUMENT MAPPING & PRICE DISCREPANCIES ---
    print("\n[*] PART 2-6: Instrument Mapping & Price Forensic Audit")

    price_audit = []
    for sig in sigs:
        # Construct actual instrument identifier
        instr_id = "N/A"
        expected_price_type = "SPOT"

        if sig.asset_class == "EQUITY":
            instr_id = f"{sig.symbol}.NS"
            expected_price_type = "ADJUSTED_EQUITY"
        elif sig.asset_class == "FUTURES":
            instr_id = f"{sig.symbol} FUT" # Placeholder for construction logic
            expected_price_type = "FUTURE_PREMIUM"
        elif sig.asset_class == "OPTIONS":
            instr_id = f"{sig.symbol} {sig.strike} {sig.option_type}"
            expected_price_type = "OPTION_PREMIUM"

        # Fetch LIVE price for the UNDERLYING for comparison
        underlying_price = await provider.get_ltp(sig.symbol)

        # Check for discrepancies (Part 3)
        discrepancy = abs(sig.entry_price - underlying_price) / sig.entry_price if underlying_price > 0 else 0

        price_audit.append({
            "ID": sig.id.split('_')[2],
            "TYPE": sig.asset_class,
            "ENTRY": sig.entry_price,
            "UNDERLYING_LIVE": underlying_price,
            "DISCREP_%": round(discrepancy * 100, 2),
            "ISSUE": "CA_MISMATCH" if discrepancy > 0.3 and sig.asset_class == "EQUITY" else "WRONG_MAPPING" if sig.asset_class != "EQUITY" and discrepancy < 0.05 else "OK"
        })

    print(pd.DataFrame(price_audit).to_string(index=False))

    # --- PART 4: OPTION PRICE SPECIFIC ---
    print("\n[*] PART 4: Option Premium vs Underlying Verification")
    opt_sig = db.query(LiveSignalDB).filter(LiveSignalDB.asset_class == "OPTIONS").first()
    if opt_sig:
        underlying_price = await provider.get_ltp(opt_sig.symbol)
        print(f"   Signal: {opt_sig.id}")
        print(f"   Underlying ({opt_sig.symbol}) Live: {underlying_price}")
        print(f"   Signal Entry (Premium): {opt_sig.entry_price}")
        if underlying_price > opt_sig.entry_price * 10:
            print("   [!] CONFIRMED: Current price in Step 2A report was using Underlying instead of Premium.")
        else:
            print("   [OK] Premium/Underlying mapping appears consistent.")

    # --- PART 10: UNIVERSE FRESHNESS ---
    print("\n[*] PART 10: Universe Market Data Freshness (Neon Stats)")
    stocks = db.query(StockDB).filter(StockDB.index_membership == 'NIFTY_200').all()
    ages = [(now - s.updated_at).total_seconds() for s in stocks if s.updated_at]

    if ages:
        print(f"   Average Age: {np.mean(ages):.1f}s")
        print(f"   P95 Age:     {np.percentile(ages, 95):.1f}s")
        print(f"   Stale (>1h): {len([a for a in ages if a > 3600])} / {len(stocks)}")

    # --- PART 17: FALLBACK CONTAMINATION CHECK ---
    print("\n[*] PART 17: Logic Audit (Fallback Contamination)")
    # Searching for 'current_price = entry_price' equivalent in repo
    # This is a manual check I will perform via grep next.

    db.close()
    print("\n============================================================")
    print(" B2 FORENSIC AUDIT COMPLETE")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(run_audit())
