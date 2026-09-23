"""
================================================================================
TradeMindAI: Safe Non-Destructive Local Database Seeder
================================================================================
Checks table content before populating sample historical OHLCV data if empty.
Ensures zero data loss for existing local tables and records.
"""

import datetime
import numpy as np
import logging
from backend.app.db.database import engine, Base, SessionLocal
from backend.app.db.models import MarketData, Watchlist, NewsArticle, TradingSignal

logger = logging.getLogger(__name__)

SEED_SYMBOLS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "LT", "ITC", "BHARTIARTL", "TATAMOTORS"
]

def seed_local_database():
    """
    Safely verifies and populates local database if empty.
    """
    logger.info("[Local Seed] Verifying database schema...")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # Check if MarketData already has content
        existing_count = session.query(MarketData).count()
        if existing_count > 0:
            logger.info(f"[Local Seed] Database already contains {existing_count} MarketData records. Skipping seed.")
            return

        logger.info("[Local Seed] Seeding local OHLCV price time-series...")
        now = datetime.datetime.utcnow()
        records = []

        for sym in SEED_SYMBOLS:
            base_p = 500.0 + (hash(sym) % 2500)
            # Add Watchlist entry
            session.add(Watchlist(symbol=sym))

            # Generate 180 daily price bars per symbol
            for day in range(180):
                dt = now - datetime.timedelta(days=(180 - day))
                variation = (np.sin(day / 15.0) * 12.0) + ((day % 5) - 2) * 1.5
                c_price = max(10.0, base_p + variation)
                records.append(MarketData(
                    symbol=sym,
                    timestamp=dt,
                    open=round(c_price - 2.0, 2),
                    high=round(c_price + 5.0, 2),
                    low=round(c_price - 4.0, 2),
                    close=round(c_price, 2),
                    volume=round(500000 + (day * 1500), 2)
                ))

            # Add sample news article for sentiment analysis
            session.add(NewsArticle(
                symbol=sym,
                title=f"{sym} reports strong quarterly earnings and robust revenue growth.",
                content=f"Quarterly financial results for {sym} exceeded institutional expectations with robust margin expansion and strong order book pipeline.",
                published_at=now - datetime.timedelta(days=2),
                sentiment_score=0.85
            ))

        session.bulk_save_objects(records)
        session.commit()
        logger.info(f"[Local Seed] Successfully seeded {len(records)} MarketData records across {len(SEED_SYMBOLS)} symbols.")

    except Exception as err:
        logger.error(f"[Local Seed] Seeding error: {err}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_local_database()
