import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB

async def generate():
    db = SessionLocal()
    print("[*] STEP 4: Generating Master Live Signals (Equity, Futures, Options)...")

    # Forensic Cleanup: Remove any existing signals with these master IDs to prevent duplicates
    # and ensure contract details are always clean (prevents 'null null' issues)
    print("[*] Cleaning up existing live master nodes...")
    db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).delete(synchronize_session=False)

    now = datetime.now()
    expiry = now + timedelta(days=12)

    signals = []

    # --- EQUITY ---
    equity_setups = [
        ("RELIANCE", "STRONG BUY", 2980.0, 3150.0, 2920.0, 92),
        ("TCS", "BUY", 4520.0, 4800.0, 4450.0, 85),
        ("INFY", "BUY", 1910.0, 2050.0, 1860.0, 88),
        ("LT", "STRONG BUY", 3550.0, 3850.0, 3480.0, 94),
        ("ITC", "BUY", 495.0, 550.0, 482.0, 82),
    ]
    for sym, rating, entry, target, stop, conviction in equity_setups:
        signals.append(LiveSignalDB(
            id=f"master_eq_{sym}_{now.strftime('%H%M%S')}", symbol=sym, timestamp=now,
            rating=rating, direction="LONG", conviction=float(conviction),
            entry_price=entry, target_price=target, stop_loss_price=stop,
            timeframe="SWING", status="ACTIVE", asset_class="EQUITY",
            model_version="TradeMind Core v2.2",
            events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat()}])
        ))

    # --- FUTURES ---
    futures_setups = [
        ("NIFTY", 24850.0, 25200.0, 24650.0, 84, 25),
        ("BANKNIFTY", 52600.0, 53800.0, 52100.0, 81, 15),
        ("RELIANCE", 3010.0, 3180.0, 2960.0, 87, 250),
    ]
    for sym, entry, target, stop, conviction, lot in futures_setups:
        signals.append(LiveSignalDB(
            id=f"master_fut_{sym}_{now.strftime('%H%M%S')}", symbol=sym, timestamp=now,
            rating="BUY", direction="LONG", conviction=float(conviction),
            entry_price=entry, target_price=target, stop_loss_price=stop,
            timeframe="INTRADAY", status="ACTIVE", asset_class="FUTURES",
            underlying_symbol=sym, expiry=expiry, lot_size=lot,
            model_version="TradeMind F&O v1.1",
            events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat()}])
        ))

    # --- OPTIONS ---
    options_setups = [
        ("NIFTY", 25000, "CE", 155.0, 280.0, 95.0, 89, 25),
        ("RELIANCE", 3100, "CE", 48.0, 95.0, 30.0, 86, 250),
        ("SBIN", 860, "CE", 18.0, 42.0, 10.0, 79, 1500)
    ]
    for sym, strike, opt_type, entry, target, stop, conviction, lot in options_setups:
        signals.append(LiveSignalDB(
            id=f"master_opt_{sym}_{strike}_{now.strftime('%H%M%S')}", symbol=sym, timestamp=now,
            rating="BUY", direction="LONG", conviction=float(conviction),
            entry_price=entry, target_price=target, stop_loss_price=stop,
            timeframe="SWING", status="ACTIVE", asset_class="OPTIONS",
            underlying_symbol=sym, strike=float(strike), option_type=opt_type, expiry=expiry, lot_size=lot,
            model_version="TradeMind F&O v1.1",
            events=json.dumps([{"type": "GENERATED", "timestamp": now.isoformat()}])
        ))

    try:
        for s in signals: db.add(s)
        db.commit()
        print(f"[SUCCESS] Generated {len(signals)} multi-segment live signals.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate())
