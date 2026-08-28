import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.core.postgres import SessionLocal, RegimeDB

async def populate_regimes():
    print("[*] Generating historical Market Regimes (NIFTY 50)...")

    # 1. Fetch History
    symbol = "^NSEI"
    prices = await container.provider.fetch_history(symbol, "max")
    if prices.empty:
        print("[!] No NIFTY data found.")
        return

    df = prices.copy()
    df.columns = [c.capitalize() for c in df.columns]
    df.index = pd.to_datetime(df.index).tz_localize(None)

    # 2. Indicators
    df['ema_200'] = df['Close'].rolling(200).mean()
    df['returns'] = df['Close'].pct_change()
    df['vol_20'] = df['returns'].rolling(20).std() * np.sqrt(252)
    median_vol = df['vol_20'].median()

    def get_regime(row):
        if pd.isna(row['ema_200']): return "UNKNOWN"
        is_bull = row['Close'] > row['ema_200']
        is_high_vol = row['vol_20'] > median_vol
        if is_bull: return "BULL_HIGH_VOL" if is_high_vol else "BULL_STABLE"
        else: return "BEAR_HIGH_VOL" if is_high_vol else "BEAR_STABLE"

    df['regime'] = df.apply(get_regime, axis=1)

    # 3. Save to DB
    with SessionLocal() as session:
        count = 0
        # Ingest only last 365 days of regimes
        last_year = df.tail(365)
        for ts, row in last_year.iterrows():
            # Check if exists
            exists = session.query(RegimeDB).filter(RegimeDB.date == ts).first()
            if not exists:
                r = RegimeDB(
                    date=ts,
                    regime=row['regime'],
                    risk_mode="RISK_ON" if "BULL" in row['regime'] else "RISK_OFF",
                    sentiment_score=0.6 if "BULL" in row['regime'] else 0.4,
                    volatility_index=float(row['vol_20'] * 100),
                    description=f"Automated historical classification: {row['regime']}"
                )
                session.add(r)
                count += 1
        session.commit()
        print(f"   [+] Generated {count} historical regimes.")

if __name__ == "__main__":
    asyncio.run(populate_regimes())
