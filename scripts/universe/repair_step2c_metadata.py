import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB

def repair():
    db = SessionLocal()
    print("[*] Repairing Metadata for 11 Master Signals (Step 2C)...")

    sigs = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    for s in sigs:
        # 1. Canonical Instrument ID & Type
        if s.asset_class == "EQUITY":
            s.instrument_type = "EQUITY"
            s.instrument_id = f"{s.symbol}.NS"
            s.underlying_symbol = s.symbol
        elif s.asset_class == "FUTURES":
            s.instrument_type = "FUTURE"
            # Standard NSE Future naming: SYMBOL + YY + MMM + FUT
            # For August 2026: NIFTY26AUGFUT
            s.instrument_id = f"{s.symbol}26AUGFUT.NS"
            s.underlying_symbol = s.symbol
        elif s.asset_class == "OPTIONS":
            s.instrument_type = "OPTION"
            # NIFTY26827C25000.NS (Estimated)
            # We use the strike/type from model
            stk = int(s.strike) if s.strike else 0
            typ = s.option_type[0] if s.option_type else 'C'
            s.instrument_id = f"{s.symbol}26827{typ}{stk}.NS"
            s.underlying_symbol = s.symbol

        # 2. Separate Underlying Symbol for Indices
        if s.symbol == "NIFTY": s.underlying_symbol = "NIFTY"
        if s.symbol == "BANKNIFTY": s.underlying_symbol = "BANKNIFTY"

        print(f"   [+] {s.symbol:<12} | ID: {s.instrument_id:<20} | Type: {s.instrument_type}")

    db.commit()
    db.close()
    print("\n[SUCCESS] Metadata Repaired.")

if __name__ == "__main__":
    repair()
