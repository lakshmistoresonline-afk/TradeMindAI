import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, StockDB, LiveSignalDB

async def generate_signals():
    print("[*] Running Precision Scoring Algorithm...")

    db = SessionLocal()
    try:
        # Fetch stocks with enriched data
        stocks = db.query(StockDB).all()

        signals_generated = 0
        for stock in stocks:
            # 1. Base technical components (simulated from analysis if exists)
            base_score = stock.ai_investment_score if stock.ai_investment_score is not None else 65.0

            # 2. Institutional Accuracy Boost (The "Final Update" Logic)
            accuracy_boost = 0
            if stock.delivery_rate > 55: accuracy_boost += 12 # Institutional Floor
            if stock.options_pcr > 1.1: accuracy_boost += 8   # Put-OI Support
            if stock.sector_alpha > 1.0: accuracy_boost += 5  # Relative Leadership

            precision_score = min(100.0, base_score + accuracy_boost)

            if stock.symbol in ["RELIANCE", "TCS", "INFY", "LT", "ITC"]:
                print(f"   [Debug] {stock.symbol}: Base={base_score}, Boost={accuracy_boost}, Total={precision_score}")

            # 3. Decision Logic (Lowered threshold for first run validation)
            if precision_score >= 70 and stock.ai_status != "INVALID":
                # Generate a Premium Signal
                signal_id = f"prec_{stock.symbol}_{datetime.utcnow().strftime('%Y%m%d%H%M')}"

                # Check for existing precision signal to avoid duplicates
                existing = db.query(LiveSignalDB).filter(
                    LiveSignalDB.symbol == stock.symbol,
                    LiveSignalDB.model_version == "TradeMind Precision v1.0"
                ).first()

                if not existing:
                    entry = stock.last_price or 0.0
                    if entry == 0: continue

                    target = entry * 1.08 # Conservative 8% Target
                    stop = entry * 0.95   # 5% Stop

                    new_signal = LiveSignalDB(
                        id=signal_id,
                        symbol=stock.symbol,
                        timestamp=datetime.utcnow(),
                        rating="STRONG BUY",
                        direction="LONG",
                        conviction=precision_score,
                        entry_price=entry,
                        target_price=target,
                        stop_loss_price=stop,
                        timeframe="SWING",
                        status="ACTIVE",
                        model_version="TradeMind Precision v1.0",
                        events=json.dumps([
                            {"type": "GENERATED", "timestamp": datetime.utcnow().isoformat(), "message": "Precision setup identified with Institutional Confirmation."}
                        ])
                    )
                    db.add(new_signal)
                    signals_generated += 1
                    print(f"   [+] Signal: {stock.symbol} | Score: {precision_score} | Rating: STRONG BUY")

        db.commit()
        print(f"[+] Total Precision Signals Generated: {signals_generated}")
    except Exception as e:
        print(f"[-] Error generating signals: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate_signals())
