import os
import sys
import asyncio

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def check():
    from backend.core.postgres import SessionLocal, LiveSignalDB

    with SessionLocal() as session:
        signals = session.query(LiveSignalDB).all()
        print(f"Total Signals: {len(signals)}")
        for s in signals:
            print(f"Symbol: {s.symbol} | Status: {s.status} | Rating: {s.rating}")

if __name__ == "__main__":
    asyncio.run(check())
