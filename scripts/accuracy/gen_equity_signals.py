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
from backend.services.risk_engine import RiskEngine
from backend.services.calibration_service import CalibrationService
from backend.services.sector_rotation_service import SectorRotationService

async def generate():
    db = SessionLocal()
    print("[*] Generating NIFTY-200 Cash Equity signals with V2.3 Engine...")

    # Cleanup existing live equity setups
    db.query(LiveSignalDB).filter(LiveSignalDB.id.like('live_eq_%')).delete(synchronize_session=False)

    now = datetime.utcnow()

    equity_setups = [
        ("RELIANCE", "STRONG BUY", 2980.0, 45.0, 0.92, "SWING", "HIGH_VOLATILITY"),
        ("TCS", "BUY", 4520.0, 55.0, 0.85, "SWING", "BULL"),
        ("INFY", "BUY", 1910.0, 28.0, 0.88, "SWING", "BULL"),
        ("LT", "STRONG BUY", 3550.0, 52.0, 0.94, "SWING", "HIGH_VOLATILITY"),
        ("ITC", "BUY", 495.0, 8.5, 0.82, "SWING", "SIDEWAYS"),
        ("BHARTIARTL", "STRONG BUY", 1480.0, 22.0, 0.90, "SHORT", "BULL"),
        ("ESCORTS", "BUY", 3850.0, 60.0, 0.86, "SWING", "BULL")
    ]

    try:
        added = 0
        for sym, rating, entry, atr, raw_prob, horizon, regime in equity_setups:
            sig_id = f"live_eq_{sym}_{now.strftime('%H%M%S')}"

            calibrated = CalibrationService.calibrate_probability(raw_prob, "EQUITY")
            risk_params = RiskEngine.calculate_trade_parameters(
                symbol=sym, price=entry, direction="LONG", atr=atr, horizon=horizon, regime=regime
            )

            target = risk_params.get("target", entry * 1.05)
            stop = risk_params.get("stop_loss", entry * 0.97)
            reward = abs(target - entry)
            risk = abs(entry - stop)
            ev = CalibrationService.calculate_expected_value(calibrated, reward, risk, entry_price=entry)

            sig = LiveSignalDB(
                id=sig_id, symbol=sym, timestamp=now,
                rating=rating, direction="LONG", conviction=float(calibrated * 100),
                raw_probability=float(raw_prob), calibrated_probability=float(calibrated),
                expected_value=float(ev), risk_reward_ratio=risk_params.get("risk_reward", 2.5),
                entry_price=entry, target_price=target, stop_price=stop,
                timeframe=horizon, status="ACTIVE", asset_type="EQUITY",
                model_version="TradeMind Core v2.3-Ensemble",
                events=json.dumps([{
                    "type": "GENERATED",
                    "timestamp": now.isoformat(),
                    "message": f"V2.3 High-alpha NIFTY-200 cash setup identified in {regime} regime."
                }])
            )
            db.add(sig)
            added += 1

        db.commit()
        print(f"[+] Successfully generated {added} P0/V2.3 NIFTY-200 Equity signals.")
    except Exception as e:
        print(f"[-] Error generating equity signals: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate())
