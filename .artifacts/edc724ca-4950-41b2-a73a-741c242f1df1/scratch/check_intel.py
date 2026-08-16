import os
import sys
import asyncio

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def check():
    from backend.core.postgres import SessionLocal, IntelReportDB, RegimeDB

    with SessionLocal() as session:
        reports = session.query(IntelReportDB).count()
        regimes = session.query(RegimeDB).count()

        print(f"Total Intel Reports: {reports}")
        print(f"Total Market Regimes: {regimes}")

        if reports > 0:
            latest = session.query(IntelReportDB).order_by(IntelReportDB.date.desc()).first()
            print(f"Latest Report: {latest.summary}")

        if regimes > 0:
            latest = session.query(RegimeDB).order_by(RegimeDB.date.desc()).first()
            print(f"Latest Regime: {latest.regime} - {latest.description}")

if __name__ == "__main__":
    asyncio.run(check())
