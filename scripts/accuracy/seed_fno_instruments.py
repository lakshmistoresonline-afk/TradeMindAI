import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, InstrumentDB

async def seed_fno():
    print("[*] Seeding Nifty 50 F&O Instruments...")

    # Representative contracts for Nifty 50 leaders
    expiry = datetime.utcnow() + timedelta(days=12) # Near month expiry

    contracts = [
        # NIFTY Index
        {"id": "nifty_25000_ce", "exchange": "NSE", "trading_symbol": "NIFTY25000CE", "groww_symbol": "NIFTY", "instrument_type": "OPTIDX", "option_type": "CE", "strike": 25000.0, "expiry": expiry},
        {"id": "nifty_24500_pe", "exchange": "NSE", "trading_symbol": "NIFTY24500PE", "groww_symbol": "NIFTY", "instrument_type": "OPTIDX", "option_type": "PE", "strike": 24500.0, "expiry": expiry},
        {"id": "nifty_fut", "exchange": "NSE", "trading_symbol": "NIFTYFUT", "groww_symbol": "NIFTY", "instrument_type": "FUTIDX", "expiry": expiry},

        # RELIANCE
        {"id": "rel_3000_ce", "exchange": "NSE", "trading_symbol": "RELIANCE3000CE", "groww_symbol": "RELIANCE", "instrument_type": "OPTSTK", "option_type": "CE", "strike": 3000.0, "expiry": expiry},
        {"id": "rel_fut", "exchange": "NSE", "trading_symbol": "RELIANCEFUT", "groww_symbol": "RELIANCE", "instrument_type": "FUTSTK", "expiry": expiry}
    ]

    db = SessionLocal()
    try:
        added = 0
        for c in contracts:
            existing = db.query(InstrumentDB).filter(InstrumentDB.id == c['id']).first()
            if not existing:
                db.add(InstrumentDB(**c))
                added += 1
        db.commit()
        print(f"[+] Seeded {added} F&O instruments.")
    except Exception as e:
        print(f"[-] Error seeding instruments: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_fno())
