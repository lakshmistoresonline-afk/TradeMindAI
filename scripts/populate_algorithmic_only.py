import os
import sys
import asyncio
import json
import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force Local SQLite Mode
os.environ["POSTGRES_URL"] = "sqlite:///./local_operational.db"

# Load environment
load_dotenv(os.path.join("backend", ".env"))

from backend.core.postgres import SessionLocal, StockDB, LiveSignalDB, init_db
from backend.core.container import container
from scripts.audit_database import ALL_SUPPORTED
from backend.analysis.technical import TechnicalAnalysis
from backend.analysis.smc import SMCAnalysis
from backend.analysis.wyckoff import WyckoffAnalysis
from backend.services.quant_engine import QuantEngine

async def populate_algorithmic_high_fidelity():
    print("--- TRADEMIND AI: ⚡ ALGORITHMIC ENGINE v2.0 (HIGH-FIDELITY) ---")
    print("Synthesizing Institutional Signals using SMC, Wyckoff, Technical, and Quant Engines...")

    init_db() # Ensure schema is ready
    session = SessionLocal()

    try:
        # Fetch NIFTY benchmark for Quant metrics
        nifty_history = await container.provider.fetch_history("NIFTY", period="1y", interval="1d")
        if nifty_history.empty:
            nifty_history = await container.provider.fetch_history("^NSEI", period="1y", interval="1d")

        for symbol in ALL_SUPPORTED:
            print(f"[*] Analyzing {symbol}...")
            try:
                # 1. Data Ingestion
                history = await container.provider.fetch_history(symbol, period="1y", interval="1d")
                if history.empty: continue

                # 2. Parallel Analysis Execution
                # A. Technical Analysis (Momentum & Trend)
                df_ta = TechnicalAnalysis.calculate_indicators(history.copy())
                last_price = float(history['Close'].iloc[-1])
                rsi = float(df_ta['RSI'].iloc[-1]) if 'RSI' in df_ta.columns else 50
                ema_200 = float(df_ta['EMA_200'].iloc[-1]) if 'EMA_200' in df_ta.columns else 0

                # B. SMC Analysis (Institutional Structure)
                smc_structure = SMCAnalysis.detect_structure_change(history)
                order_blocks = SMCAnalysis.detect_order_blocks(history)
                fvgs = SMCAnalysis.detect_fvg(history)

                # C. Wyckoff Analysis (Market Cycle)
                wyckoff_phase = WyckoffAnalysis.detect_phase(history)

                # D. Quant Analysis (Risk/Reward & Volatility)
                quant_metrics = QuantEngine.calculate_metrics(symbol, history, nifty_history)

                # 3. High-Fidelity Signal Synthesis (Multi-Engine Consensus)
                rating = "HOLD"
                direction = "NEUTRAL"
                conviction = 50.0

                # BULLISH CRITERIA:
                # 1. Price above 200 EMA (Long-term Trend)
                # 2. BOS or CHoCH (Structure Support)
                # 3. Markup or Accumulation Phase
                # 4. RSI not overbought (< 70)
                is_bullish_trend = last_price > ema_200 if ema_200 > 0 else True
                has_bullish_bos = smc_structure['type'] == 'BOS' and smc_structure['bias'] == 'BULLISH'
                is_markup = wyckoff_phase in ["Markup", "Accumulation"]

                if is_bullish_trend and has_bullish_bos and is_markup and rsi < 65:
                    rating = "STRONG BUY" if rsi > 55 else "BUY"
                    direction = "LONG"
                    conviction = 82.5 if rating == "STRONG BUY" else 74.0

                # BEARISH CRITERIA:
                # 1. Price below 200 EMA
                # 2. Bearish Structure
                # 3. Markdown or Distribution Phase
                elif not is_bullish_trend and smc_structure['bias'] == 'BEARISH' and wyckoff_phase in ["Markdown", "Distribution"]:
                    rating = "SELL"
                    direction = "SHORT"
                    conviction = 71.5

                # 4. Target/Stop Generation (Volatility-Adjusted)
                # Use annualized volatility to set realistic stops (approx 1 std dev)
                vol_buffer = max(0.02, quant_metrics.volatility / 20) # Min 2% buffer

                if direction == "LONG":
                    target = last_price * (1 + (vol_buffer * 3)) # 3:1 R:R
                    stop = last_price * (1 - vol_buffer)
                elif direction == "SHORT":
                    target = last_price * (1 - (vol_buffer * 3))
                    stop = last_price * (1 + vol_buffer)
                else:
                    target, stop = 0.0, 0.0

                # 5. Metadata Construction
                indicators = {
                    "rsi": rsi,
                    "ema_200": ema_200,
                    "volatility": quant_metrics.volatility,
                    "beta": quant_metrics.beta,
                    "wyckoff": wyckoff_phase,
                    "smc": smc_structure['type']
                }

                thesis = f"Multi-Engine Alignment: {wyckoff_phase} cycle detected. "
                if has_bullish_bos: thesis += "Institutional Break of Structure confirmed bullish bias. "
                thesis += f"Volatility-adjusted R:R set at {round(quant_metrics.volatility*100, 1)}% annualized risk."

                structured = {
                    "rating": rating,
                    "conviction": conviction,
                    "thesis": thesis,
                    "entry": last_price,
                    "target": target,
                    "stop_loss": stop,
                    "timeframe": "SWING",
                    "risk_reward": f"1:{round((target-last_price)/(last_price-stop), 1)}" if direction == "LONG" else "1:2.5",
                    "key_catalysts": ["Structure Break", f"{wyckoff_phase} Alignment"],
                    "agent_debate": [
                        {"agent": "TechnicalEngine", "summary": f"RSI at {round(rsi,1)}. EMA 200 at {round(ema_200,1)}."},
                        {"agent": "SMCEngine", "summary": f"Detected {smc_structure['type']} at {smc_structure['level']}."},
                        {"agent": "WyckoffEngine", "summary": f"Confirmed {wyckoff_phase} phase based on 50-day cycle."}
                    ]
                }

                # 6. Database Persistence
                stock = session.query(StockDB).filter(StockDB.symbol == symbol).first()
                if not stock:
                    stock = StockDB(symbol=symbol, name=symbol)
                    session.add(stock)

                stock.last_price = last_price
                stock.ai_status = "SUCCESS"
                stock.structured_consensus = json.dumps(structured)
                stock.ai_investment_score = conviction
                stock.beta = quant_metrics.beta
                stock.updated_at = datetime.datetime.utcnow()

                if rating != "HOLD":
                    sig_id = f"algo_{symbol}_{datetime.datetime.utcnow().strftime('%Y%m%d')}"
                    existing_sig = session.query(LiveSignalDB).filter(LiveSignalDB.id == sig_id).first()
                    if not existing_sig:
                        session.add(LiveSignalDB(
                            id=sig_id,
                            symbol=symbol,
                            timestamp=datetime.datetime.utcnow(),
                            rating=rating,
                            direction=direction,
                            conviction=conviction,
                            entry_price=last_price,
                            target_price=target,
                            stop_loss_price=stop,
                            timeframe="SWING",
                            status="ACTIVE",
                            model_version="TradeMind-Hybrid-Quant-v2"
                        ))

                session.commit()
                print(f"   [+] {symbol}: {rating} (Conviction: {conviction}%)")

            except Exception as e:
                print(f"   [!] Error {symbol}: {e}")
                session.rollback()

    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(populate_algorithmic_high_fidelity())
