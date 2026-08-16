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
    print("[*] Generating Options signals...")

    # Cleanup existing live options setups
    db.query(LiveSignalDB).filter(LiveSignalDB.id.like('live_opt_%')).delete(synchronize_session=False)

    now = datetime.utcnow()
    expiry = now + timedelta(days=12)

    options_setups = [
        ("NIFTY", 25000, "CE", "BUY", 155.0, 280.0, 95.0, 89, 25),
        ("RELIANCE", 3100, "CE", "BUY", 48.0, 95.0, 30.0, 86, 250),
        ("HDFCBANK", 1650, "PE", "SELL", 35.0, 10.0, 60.0, 82, 550), # Shorting PE is Bullish
        ("TCS", 4600, "CE", "BUY", 125.0, 210.0, 80.0, 85, 175),
        ("SBIN", 860, "CE", "BUY", 18.0, 42.0, 10.0, 79, 1500)
    ]

    try:
        added = 0
        for sym, strike, opt_type, rating, entry, target, stop, conviction, lot in options_setups:
            sig_id = f"live_opt_{sym}_{strike}_{now.strftime('%H%M%S')}"

            sig = LiveSignalDB(
                id=sig_id, symbol=sym, timestamp=now,
                rating=rating, direction="LONG" if rating == "BUY" else "SHORT", conviction=float(conviction),
                entry_price=entry, target_price=target, stop_loss_price=stop,
                timeframe="SWING", status="ACTIVE", asset_class="OPTIONS",
                underlying_symbol=sym, strike=float(strike), option_type=opt_type, expiry=expiry, lot_size=lot,
                model_version="TradeMind F&O v1.1",
                events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat(), "message": "High gamma premium breakout confirmed."}])
            )
            db.add(sig)
            added += 1

        db.commit()
        print(f"[+] Successfully generated {added} Options signals.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate())
