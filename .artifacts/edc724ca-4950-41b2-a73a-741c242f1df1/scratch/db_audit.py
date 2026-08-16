import os
import sys
import asyncio
import json

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def audit():
    from backend.core.container import container
    from backend.core.postgres import SessionLocal, StockDB, LiveSignalDB
    from sqlalchemy import text

    with SessionLocal() as session:
        total_stocks = session.query(StockDB).count()
        analyzed_stocks = session.query(StockDB).filter(StockDB.analysis != None).all()
        live_signals = session.query(LiveSignalDB).count()
        active_signals = session.query(LiveSignalDB).filter(LiveSignalDB.status.in_(["ACTIVE", "WAITING_FOR_ENTRY", "ENTRY_TRIGGERED"])).count()

        print(f"Total Stocks: {total_stocks}")
        print(f"Stocks with Analysis: {len(analyzed_stocks)}")
        print(f"Total Live Signals: {live_signals}")
        print(f"Active Live Signals: {active_signals}")

        if analyzed_stocks:
            print("\nRecent Analyses in Stocks Table:")
            for s in analyzed_stocks[:10]:
                rating = "N/A"
                if s.structured_consensus:
                    try:
                        # structured_consensus is stored as JSON string in DB
                        if isinstance(s.structured_consensus, str):
                            sc = json.loads(s.structured_consensus)
                        else:
                            sc = s.structured_consensus
                        rating = sc.get("rating", "N/A")
                    except: pass
                print(f"  {s.symbol}: Rating={rating}, Score={s.ai_investment_score}")

if __name__ == "__main__":
    asyncio.run(audit())
