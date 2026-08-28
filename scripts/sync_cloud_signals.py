import os
import sys
import asyncio
import json
import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join("backend", ".env"))

# Target the Cloud URL explicitly
db_url = os.getenv("POSTGRES_URL")
if not db_url or "sqlite" in db_url:
    print("[!] Error: Cloud database URL not found in .env")
    sys.exit(1)

# Fix postgres prefix for SQLAlchemy
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

print(f"[*] TARGETING CLOUD DATABASE: {db_url[:25]}...")

from backend.core.postgres import SessionLocal, StockDB, LiveSignalDB, engine as local_engine
from backend.core.container import container
from scripts.audit_database import ALL_SUPPORTED
from backend.analysis.technical import TechnicalAnalysis
from backend.analysis.smc import SMCAnalysis
from backend.analysis.wyckoff import WyckoffAnalysis
from backend.services.quant_engine import QuantEngine

async def sync_production_signals():
    print("\n--- TRADEMIND AI: ☁️ CLOUD SIGNAL SYNCHRONIZATION ENGINE ---")

    # We use a custom engine to ensure we are targeting the cloud regardless of settings.py
    cloud_engine = create_engine(db_url)
    from sqlalchemy.orm import sessionmaker
    CloudSession = sessionmaker(bind=cloud_engine)
    session = CloudSession()

    try:
        # Fetch NIFTY benchmark
        nifty_history = await container.provider.fetch_history("NIFTY", period="1y", interval="1d")

        for symbol in ALL_SUPPORTED:
            print(f"[*] Processing {symbol}...")
            try:
                # 1. Fetch History
                history = await container.provider.fetch_history(symbol, period="1y", interval="1d")
                if history.empty: continue

                # 2. Multi-Engine Analysis
                df_ta = TechnicalAnalysis.calculate_indicators(history.copy())
                last_price = float(history['Close'].iloc[-1])
                rsi = float(df_ta['RSI'].iloc[-1]) if 'RSI' in df_ta.columns else 50
                ema_200 = float(df_ta['EMA_200'].iloc[-1]) if 'EMA_200' in df_ta.columns else 0

                smc_structure = SMCAnalysis.detect_structure_change(history)
                wyckoff_phase = WyckoffAnalysis.detect_phase(history)
                quant_metrics = QuantEngine.calculate_metrics(symbol, history, nifty_history)

                # 3. Decision Logic
                rating = "HOLD"
                direction = "NEUTRAL"
                conviction = 50.0

                is_bullish_trend = last_price > ema_200 if ema_200 > 0 else True
                has_bullish_bos = smc_structure['type'] == 'BOS' and smc_structure['bias'] == 'BULLISH'

                if is_bullish_trend and has_bullish_bos and rsi < 65:
                    rating = "BUY"
                    direction = "LONG"
                    conviction = 76.0
                elif not is_bullish_trend and smc_structure['bias'] == 'BEARISH':
                    rating = "SELL"
                    direction = "SHORT"
                    conviction = 70.5

                # 4. Volatility-Adjusted Prices (Prevents NaN)
                vol_buffer = max(0.02, quant_metrics.volatility / 20)
                target = last_price * (1 + (vol_buffer * 3)) if direction == "LONG" else last_price * (1 - (vol_buffer * 3))
                stop = last_price * (1 - vol_buffer) if direction == "LONG" else last_price * (1 + vol_buffer)

                if direction == "NEUTRAL": target, stop = 0, 0

                # 5. Build Cloud Payload
                structured = {
                    "rating": rating,
                    "conviction": conviction,
                    "thesis": f"Cloud Reconciled: {wyckoff_phase} phase with SMC {smc_structure['type']} confirmation.",
                    "entry": last_price,
                    "target": target,
                    "stop_loss": stop,
                    "timeframe": "SWING",
                    "risk_reward": "1:3.0"
                }

                # 6. Atomic Cloud Update
                db_stock = session.query(StockDB).filter(StockDB.symbol == symbol).first()
                if not db_stock:
                    db_stock = StockDB(symbol=symbol, name=symbol)
                    session.add(db_stock)

                db_stock.last_price = last_price
                db_stock.ai_status = "SUCCESS"
                db_stock.structured_consensus = json.dumps(structured)
                db_stock.updated_at = datetime.datetime.utcnow()

                # Add to live signals feed
                if rating != "HOLD":
                    sig_id = f"cloud_sync_{symbol}_{datetime.datetime.utcnow().strftime('%Y%m%d')}"
                    existing_sig = session.query(LiveSignalDB).filter(LiveSignalDB.id == sig_id).first()
                    if not existing_sig:
                        session.add(LiveSignalDB(
                            id=sig_id, symbol=symbol, timestamp=datetime.datetime.utcnow(),
                            rating=rating, direction=direction, conviction=conviction,
                            entry_price=last_price, target_price=target, stop_loss_price=stop,
                            status="ACTIVE", model_version="TradeMind-Cloud-Quant-v2"
                        ))

                session.commit()
                print(f"   [+] {symbol}: Success ({rating})")

            except Exception as e:
                print(f"   [!] Error {symbol}: {e}")
                session.rollback()

    finally:
        session.close()

    print("\n--- CLOUD UPDATE COMPLETE: Dashboard is now synchronized. ---")

if __name__ == "__main__":
    asyncio.run(sync_production_signals())
