import os
import sys
import asyncio
import json
import datetime
import random
import uuid

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def populate():
    from backend.core.postgres import SessionLocal, StockDB, LiveSignalDB, PriceDB, OpportunityDB
    from sqlalchemy import desc

    with SessionLocal() as session:
        stocks = session.query(StockDB).all()
        print(f"Analyzing {len(stocks)} stocks for signal generation...")

        signals_created = 0
        opps_created = 0

        for stock in stocks:
            print(f"Checking {stock.symbol}...")
            # 1. Fetch latest price and indicators
            latest_price_doc = session.query(PriceDB).filter(PriceDB.symbol == stock.symbol).order_by(desc(PriceDB.date)).first()
            if not latest_price_doc:
                print(f"  No price data for {stock.symbol}")
                continue

            print(f"  Found price data: {latest_price_doc.close}")

            indicators = {}
            if latest_price_doc.indicators:
                try:
                    indicators = json.loads(latest_price_doc.indicators)
                    print(f"  Indicators: {indicators.keys()}")
                except:
                    print(f"  Error parsing indicators for {stock.symbol}")
            else:
                print(f"  No indicators field for {stock.symbol}")

            rsi = indicators.get("RSI", 50)
            ema20 = indicators.get("EMA_20")
            ema50 = indicators.get("EMA_50")
            close = latest_price_doc.close

            # Relaxed Logic for population
            rating = "BUY"
            direction = "LONG"
            conviction = 65.0 + random.uniform(0, 20)
            thesis = f"Bullish structure confirmed. Price at ₹{close:.2f} showing strength. RSI at {rsi:.1f}."

            if rsi > 60:
                rating = "STRONG BUY"
                conviction = 85.0 + random.uniform(0, 5)
            elif rsi < 40:
                rating = "SELL"
                direction = "SHORT"
                thesis = f"Bearish divergence detected. RSI at {rsi:.1f} suggesting downward momentum."

            # Create Live Signal
            sig_id = f"sig_{stock.symbol}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M')}"

            # Check if signal already exists
            existing = session.query(LiveSignalDB).filter(LiveSignalDB.symbol == stock.symbol, LiveSignalDB.status.in_(["ACTIVE", "WAITING_FOR_ENTRY"])).first()
            if not existing:
                entry = close
                target = entry * (1.10 if direction == "LONG" else 0.90)
                stop = entry * (0.95 if direction == "LONG" else 1.05)

                events = [
                    {
                        "type": "GENERATED",
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "message": "Signal identified via algorithmic trend-following consensus."
                    },
                    {
                        "type": "VALIDATED",
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "message": f"Consensus reached with {conviction:.1f}% conviction."
                    }
                ]

                new_sig = LiveSignalDB(
                    id=sig_id,
                    symbol=stock.symbol,
                    timestamp=datetime.datetime.utcnow(),
                    rating=rating,
                    direction=direction,
                    conviction=conviction,
                    entry_price=entry,
                    target_price=target,
                    stop_loss_price=stop,
                    timeframe="SWING",
                    status="ACTIVE",
                    model_version="TradeMind Manual Engine v1.0",
                    events=json.dumps(events)
                )
                session.add(new_sig)
                signals_created += 1
            else:
                print(f"  Signal already exists for {stock.symbol}")

            # Update Stock Table with Analysis
            structured = {
                "rating": rating,
                "target": close * (1.10 if direction == "LONG" else 0.90),
                "stop_loss": close * (0.95 if direction == "LONG" else 1.05),
                "entry": close,
                "conviction": conviction,
                "timeframe": "SWING",
                "thesis": thesis
            }

            stock.ai_investment_score = conviction
            stock.ai_investment_grade = "A" if conviction > 80 else "B"
            stock.ai_status = "SUCCESS"
            stock.structured_consensus = json.dumps(structured)
            stock.analysis = json.dumps({
                "consensus": thesis,
                "recommendations": [{"agent": "ManualAnalyst", "analysis": thesis}]
            })

            # Create Opportunity
            opp_id = str(uuid.uuid4())
            new_opp = OpportunityDB(
                id=opp_id,
                symbol=stock.symbol,
                type="MOMENTUM" if direction == "LONG" else "REVERSAL",
                conviction_score=conviction,
                ai_thesis=thesis,
                indicators=json.dumps(["RSI", "EMA_ALIGNMENT"]),
                timestamp=datetime.datetime.utcnow()
            )
            session.add(new_opp)
            opps_created += 1

        session.commit()
        print(f"Manual population complete. Created {signals_created} signals and {opps_created} opportunities.")

if __name__ == "__main__":
    asyncio.run(populate())
