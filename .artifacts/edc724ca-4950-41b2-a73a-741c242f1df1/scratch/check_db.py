import os
import sys
import asyncio

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def check():
    from backend.core.container import container
    from backend.core.postgres import SessionLocal, StockDB, LiveSignalDB

    with SessionLocal() as session:
        stocks_with_analysis = session.query(StockDB).filter(StockDB.analysis != None).count()
        total_stocks = session.query(StockDB).count()
        live_signals = session.query(LiveSignalDB).count()
        active_signals = session.query(LiveSignalDB).filter(LiveSignalDB.status.in_(["ACTIVE", "WAITING_FOR_ENTRY", "ENTRY_TRIGGERED"])).count()

        print(f"Total Stocks: {total_stocks}")
        print(f"Stocks with analysis: {stocks_with_analysis}")
        print(f"Total Live Signals: {live_signals}")
        print(f"Active Live Signals: {active_signals}")

        if active_signals > 0:
            signals = session.query(LiveSignalDB).filter(LiveSignalDB.status.in_(["ACTIVE", "WAITING_FOR_ENTRY", "ENTRY_TRIGGERED"])).limit(5).all()
            for s in signals:
                print(f"Signal: {s.symbol} | {s.rating} | {s.direction} | {s.status}")

if __name__ == "__main__":
    asyncio.run(check())
