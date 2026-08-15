import os
import sys
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB

async def seed_signals():
    print("[*] Generating Comprehensive F&O signals (Live + History)...")

    now = datetime.utcnow()
    expiry = now + timedelta(days=12)
    hist_date = now - timedelta(days=5)

    signals = [
        # --- LIVE OPTIONS ---
        LiveSignalDB(
            id=str(uuid.uuid4()), symbol="RELIANCE", timestamp=now, rating="BUY", direction="LONG", conviction=88.5,
            entry_price=45.2, target_price=75.0, stop_loss_price=30.0, timeframe="SWING", status="ACTIVE",
            asset_class="OPTIONS", underlying_symbol="RELIANCE", strike=3000.0, option_type="CE", expiry=expiry, lot_size=250,
            model_version="TradeMind F&O v1.1", events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat(), "message": "Institutional buildup confirmed."}])
        ),
        LiveSignalDB(
            id=str(uuid.uuid4()), symbol="TCS", timestamp=now - timedelta(hours=2), rating="BUY", direction="LONG", conviction=74.2,
            entry_price=120.5, target_price=180.0, stop_loss_price=95.0, timeframe="SWING", status="WAITING_FOR_ENTRY",
            asset_class="OPTIONS", underlying_symbol="TCS", strike=4500.0, option_type="CE", expiry=expiry, lot_size=175,
            model_version="TradeMind F&O v1.1", events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat()}])
        ),

        # --- LIVE FUTURES ---
        LiveSignalDB(
            id=str(uuid.uuid4()), symbol="NIFTY", timestamp=now - timedelta(hours=1), rating="BUY", direction="LONG", conviction=82.0,
            entry_price=24850.0, target_price=25200.0, stop_loss_price=24650.0, timeframe="INTRADAY", status="ACTIVE",
            asset_class="FUTURES", underlying_symbol="NIFTY", expiry=expiry, lot_size=25,
            model_version="TradeMind F&O v1.1", events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat()}])
        ),
        LiveSignalDB(
            id=str(uuid.uuid4()), symbol="BANKNIFTY", timestamp=now - timedelta(hours=4), rating="SELL", direction="SHORT", conviction=79.5,
            entry_price=52500.0, target_price=51800.0, stop_loss_price=52850.0, timeframe="INTRADAY", status="ACTIVE",
            asset_class="FUTURES", underlying_symbol="BANKNIFTY", expiry=expiry, lot_size=15,
            model_version="TradeMind F&O v1.1", events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat()}])
        ),

        # --- HISTORICAL (RESOLVED) ---
        LiveSignalDB(
            id=str(uuid.uuid4()), symbol="INFY", timestamp=hist_date, rating="BUY", direction="LONG", conviction=85.0,
            entry_price=35.0, target_price=55.0, stop_loss_price=25.0, timeframe="SWING", status="TARGET_HIT",
            asset_class="OPTIONS", underlying_symbol="INFY", strike=1900.0, option_type="CE", expiry=now, lot_size=400,
            outcome_date=now - timedelta(days=1), profit_pct=57.14, trigger_price=35.0,
            model_version="TradeMind F&O v1.1", events=json.dumps([{"type": "TARGET_HIT", "timestamp": now.isoformat()}])
        ),
        LiveSignalDB(
            id=str(uuid.uuid4()), symbol="SBIN", timestamp=hist_date - timedelta(days=2), rating="BUY", direction="LONG", conviction=71.0,
            entry_price=820.0, target_price=880.0, stop_loss_price=795.0, timeframe="SWING", status="STOP_LOSS",
            asset_class="FUTURES", underlying_symbol="SBIN", expiry=now, lot_size=1500,
            outcome_date=now - timedelta(days=3), profit_pct=-3.05, trigger_price=820.0,
            model_version="TradeMind F&O v1.1", events=json.dumps([{"type": "STOP_LOSS", "timestamp": now.isoformat()}])
        ),
        LiveSignalDB(
            id=str(uuid.uuid4()), symbol="NIFTY", timestamp=hist_date - timedelta(days=5), rating="SELL", direction="SHORT", conviction=89.2,
            entry_price=150.0, target_price=80.0, stop_loss_price=190.0, timeframe="SWING", status="TARGET_HIT",
            asset_class="OPTIONS", underlying_symbol="NIFTY", strike=24000.0, option_type="PE", expiry=now, lot_size=25,
            outcome_date=now - timedelta(days=4), profit_pct=46.67, trigger_price=150.0,
            model_version="TradeMind F&O v1.1", events=json.dumps([{"type": "TARGET_HIT", "timestamp": now.isoformat()}])
        )
    ]

    db = SessionLocal()
    try:
        for s in signals:
            db.add(s)
        db.commit()
        print(f"[+] Seeded {len(signals)} F&O signals.")
    except Exception as e:
        print(f"[-] Error seeding signals: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_signals())
