import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB

async def seed_signals():
    print("[*] Generating F&O signals for UI verification...")

    expiry = datetime.utcnow() + timedelta(days=12)

    signals = [
        # Standalone Options Call
        LiveSignalDB(
            id="fno_rel_3000ce",
            symbol="RELIANCE",
            timestamp=datetime.utcnow(),
            rating="BUY",
            direction="LONG",
            conviction=88.5,
            entry_price=45.2, # Option Premium
            target_price=75.0,
            stop_loss_price=30.0,
            timeframe="SWING",
            status="ACTIVE",
            asset_class="OPTIONS",
            underlying_symbol="RELIANCE",
            strike=3000.0,
            option_type="CE",
            expiry=expiry,
            lot_size=250,
            model_version="TradeMind F&O v1.0",
            events=json.dumps([{"type": "GENERATED", "timestamp": datetime.utcnow().isoformat(), "message": "Heavy Put writing detected at 2900 floor."}])
        ),
        # Standalone Futures Call
        LiveSignalDB(
            id="fno_nifty_fut",
            symbol="NIFTY",
            timestamp=datetime.utcnow(),
            rating="BUY",
            direction="LONG",
            conviction=76.2,
            entry_price=24800.0,
            target_price=25200.0,
            stop_loss_price=24650.0,
            timeframe="INTRADAY",
            status="ACTIVE",
            asset_class="FUTURES",
            underlying_symbol="NIFTY",
            expiry=expiry,
            lot_size=25,
            model_version="TradeMind F&O v1.0",
            events=json.dumps([{"type": "GENERATED", "timestamp": datetime.utcnow().isoformat(), "message": "Long buildup with positive basis."}])
        )
    ]

    db = SessionLocal()
    try:
        added = 0
        for s in signals:
            existing = db.query(LiveSignalDB).filter(LiveSignalDB.id == s.id).first()
            if not existing:
                db.add(s)
                added += 1
        db.commit()
        print(f"[+] Generated {added} F&O signals.")
    except Exception as e:
        print(f"[-] Error seeding signals: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_signals())
