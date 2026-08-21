import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from yahooquery import Ticker
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv = lambda: None # Mock for now or import real one

from backend.core.postgres import SessionLocal, PriceDB, StockDB

async def backfill():
    symbols = ["GUJGASLTD", "LTIM", "PEL", "TATAMOTORS"]
    mapping = {
        "PEL": "PEL.NS",
        "TATAMOTORS": "TATAMOTORS.NS",
        "GUJGASLTD": "GUJGASLTD.NS",
        "LTIM": "LTIM.NS"
    }

    print("--- TRADEMIND AI DATA BACKFILL ---")

    for sym in symbols:
        ticker = mapping[sym]
        print(f"[*] Processing {sym} ({ticker})...")

        # Try yfinance first with session
        try:
            import requests
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            t = yf.Ticker(ticker, session=session)
            df = t.history(period="2y")

            if df.empty:
                # Try YahooQuery
                print(f"   [!] yfinance empty, trying yahooquery...")
                yq = Ticker(ticker)
                df = yq.history(period="2y")
                if not df.empty and 'close' in df.columns:
                     if isinstance(df.index, pd.MultiIndex):
                         df = df.reset_index(level=0, drop=True)
                     df.index = pd.to_datetime(df.index)
                     col_map = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
                     df = df.rename(columns=col_map)

            if df.empty:
                print(f"   [FAIL] Could not fetch data for {sym}")
                continue

            print(f"   [SUCCESS] Fetched {len(df)} rows.")

            # Save to SQLite
            with SessionLocal() as db_session:
                # 1. Update Stock Master
                stock = db_session.query(StockDB).filter(StockDB.symbol == sym).first()
                if stock:
                    stock.last_price = float(df['Close'].iloc[-1])
                    stock.updated_at = datetime.utcnow()

                # 2. Bulk Insert Prices
                from backend.domain.models.stock import StockPrice
                # We reuse the logic from StockService if possible, or just raw SQL
                count = 0
                for index, row in df.iterrows():
                    # Check if exists
                    existing = db_session.query(PriceDB).filter(PriceDB.symbol == sym, PriceDB.date == index).first()
                    if not existing:
                        p = PriceDB(
                            symbol=sym,
                            date=index,
                            open=float(row['Open']),
                            high=float(row['High']),
                            low=float(row['Low']),
                            close=float(row['Close']),
                            volume=int(row['Volume']) if not pd.isna(row['Volume']) else 0,
                            source="backfill"
                        )
                        db_session.add(p)
                        count += 1

                db_session.commit()
                print(f"   [DB] Inserted {count} new price records.")

        except Exception as e:
            print(f"   [ERROR] {sym}: {e}")

if __name__ == "__main__":
    asyncio.run(backfill())
