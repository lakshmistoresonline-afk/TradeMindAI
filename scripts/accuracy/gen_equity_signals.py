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
    print("[*] Generating Equity signals...")

    # Cleanup existing live equity setups
    db.query(LiveSignalDB).filter(LiveSignalDB.id.like('live_eq_%')).delete(synchronize_session=False)

    now = datetime.utcnow()

    equity_setups = [
        ("RELIANCE", "STRONG BUY", 2980.0, 3150.0, 2920.0, 92),
        ("TCS", "BUY", 4520.0, 4800.0, 4450.0, 85),
        ("INFY", "BUY", 1910.0, 2050.0, 1860.0, 88),
        ("LT", "STRONG BUY", 3550.0, 3850.0, 3480.0, 94),
        ("ITC", "BUY", 495.0, 550.0, 482.0, 82),
        ("BHARTIARTL", "STRONG BUY", 1480.0, 1650.0, 1420.0, 90),
        ("ESCORTS", "BUY", 3850.0, 4200.0, 3750.0, 86)
    ]

    try:
        added = 0
        for sym, rating, entry, target, stop, conviction in equity_setups:
            sig_id = f"live_eq_{sym}_{now.strftime('%H%M%S')}"

            sig = LiveSignalDB(
                id=sig_id, symbol=sym, timestamp=now,
                rating=rating, direction="LONG", conviction=float(conviction),
                entry_price=entry, target_price=target, stop_loss_price=stop,
                timeframe="SWING", status="ACTIVE", asset_class="EQUITY",
                model_version="TradeMind Core v2.2",
                events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat(), "message": "High-alpha cash setup identified."}])
            )
            db.add(sig)
            added += 1

        db.commit()
        print(f"[+] Successfully generated {added} Equity signals.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate())
