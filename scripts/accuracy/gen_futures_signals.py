import os
import sys
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB

async def generate():
    db = SessionLocal()
    print("[*] Generating Futures signals...")

    # Cleanup existing live futures setups
    db.query(LiveSignalDB).filter(LiveSignalDB.id.like('live_fut_%')).delete(synchronize_session=False)

    now = datetime.utcnow()
    expiry = now + timedelta(days=15)

    futures_setups = [
        ("NIFTY", "BUY", 24850.0, 25200.0, 24650.0, 84, 25),
        ("BANKNIFTY", "BUY", 52600.0, 53800.0, 52100.0, 81, 15),
        ("RELIANCE", "BUY", 3010.0, 3180.0, 2960.0, 87, 250),
        ("TCS", "BUY", 4580.0, 4750.0, 4490.0, 83, 175)
    ]

    try:
        added = 0
        for sym, rating, entry, target, stop, conviction, lot in futures_setups:
            sig_id = f"live_fut_{sym}_{now.strftime('%H%M%S')}"

            sig = LiveSignalDB(
                id=sig_id, symbol=sym, timestamp=now,
                rating=rating, direction="LONG", conviction=float(conviction),
                entry_price=entry, target_price=target, stop_loss_price=stop,
                timeframe="INTRADAY", status="ACTIVE", asset_class="FUTURES",
                underlying_symbol=sym, expiry=expiry, lot_size=lot,
                model_version="TradeMind F&O v1.1",
                events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat(), "message": "Long buildup with positive basis detected."}])
            )
            db.add(sig)
            added += 1

        db.commit()
        print(f"[+] Successfully generated {added} Futures signals.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate())
