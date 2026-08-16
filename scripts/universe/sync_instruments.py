import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import InstrumentDB

async def sync_instruments():
    print("[*] Syncing real F&O instruments from provider...")
    provider = container.provider
    session_factory = container.repository.session_factory

    try:
        instruments = await provider.get_instruments()
        if not instruments:
            print("[!] No instruments returned from provider.")
            return

        print(f"[*] Found {len(instruments)} instruments. Updating master table...")

        with session_factory() as session:
            # We don't purge everything here, we update/insert to preserve history if needed,
            # but for a fresh sync, we ensure we have the latest.

            count = 0
            for inst in instruments:
                inst_id = inst.get("id") or inst.get("groww_symbol")
                if not inst_id: continue

                db_inst = session.query(InstrumentDB).filter(InstrumentDB.id == inst_id).first()
                if not db_inst:
                    db_inst = InstrumentDB(id=inst_id)
                    session.add(db_inst)

                db_inst.exchange = inst.get("exchange", "NSE")
                db_inst.trading_symbol = inst.get("trading_symbol") or inst.get("symbol")
                db_inst.segment = inst.get("segment", "CASH")
                db_inst.instrument_type = inst.get("instrument_type", "EQUITY")
                db_inst.groww_symbol = inst.get("groww_symbol") or inst_id
                db_inst.underlying_symbol = inst.get("underlying_symbol")

                expiry = inst.get("expiry")
                if expiry and isinstance(expiry, (int, float)):
                    db_inst.expiry = datetime.fromtimestamp(expiry / 1000.0)
                elif isinstance(expiry, str):
                    try: db_inst.expiry = datetime.fromisoformat(expiry)
                    except: pass

                db_inst.strike = float(inst.get("strike", 0))
                db_inst.option_type = inst.get("option_type")
                db_inst.lot_size = inst.get("lot_size")
                db_inst.tick_size = inst.get("tick_size")
                db_inst.source = os.getenv("MARKET_DATA_PROVIDER", "yfinance")
                db_inst.last_updated = datetime.utcnow()
                count += 1

            session.commit()
            print(f"[SUCCESS] Synced {count} instruments to database.")

    except Exception as e:
        print(f"[!] Error syncing instruments: {e}")

if __name__ == "__main__":
    asyncio.run(sync_instruments())
