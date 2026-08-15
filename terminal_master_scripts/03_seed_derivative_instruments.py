import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, InstrumentDB

async def seed():
    print("[*] STEP 3: Seeding F&O Instrument Master...")

    expiry = datetime.now() + timedelta(days=12) # Aug Expiry

    contracts = [
        # Indices
        {"id": "nifty_aug_fut", "exchange": "NSE", "trading_symbol": "NIFTY26AUGFUT", "groww_symbol": "NIFTY", "instrument_type": "FUTIDX", "segment": "FUTURES", "expiry": expiry},
        {"id": "nifty_25000_ce", "exchange": "NSE", "trading_symbol": "NIFTY25000CE", "groww_symbol": "NIFTY", "instrument_type": "OPTIDX", "segment": "OPTIONS", "option_type": "CE", "strike": 25000.0, "expiry": expiry},
        {"id": "bnifty_aug_fut", "exchange": "NSE", "trading_symbol": "BANKNIFTY26AUGFUT", "groww_symbol": "BANKNIFTY", "instrument_type": "FUTIDX", "segment": "FUTURES", "expiry": expiry},

        # Stocks
        {"id": "rel_aug_fut", "exchange": "NSE", "trading_symbol": "RELIANCE26AUGFUT", "groww_symbol": "RELIANCE", "instrument_type": "FUTSTK", "segment": "FUTURES", "expiry": expiry},
        {"id": "rel_3100_ce", "exchange": "NSE", "trading_symbol": "RELIANCE3100CE", "groww_symbol": "RELIANCE", "instrument_type": "OPTSTK", "segment": "OPTIONS", "option_type": "CE", "strike": 3100.0, "expiry": expiry},
        {"id": "tcs_aug_fut", "exchange": "NSE", "trading_symbol": "TCS26AUGFUT", "groww_symbol": "TCS", "instrument_type": "FUTSTK", "segment": "FUTURES", "expiry": expiry},
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
        print(f"[SUCCESS] Seeded {added} derivative instruments.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed())
