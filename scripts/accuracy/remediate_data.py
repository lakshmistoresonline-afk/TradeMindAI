import os
import sys
import asyncio
import json
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from yahooquery import Ticker
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.analysis.technical import TechnicalAnalysis

async def fetch_history_robust(symbol: str, period="5y"):
    mapping = {
        "PEL": "PEL.NS",
        "TATAMOTORS": "TATAMOTORS.NS", # Try standard first
        "GUJGASLTD": "GUJGASLTD.NS",
        "LTIM": "LTIM.NS"
    }
    ticker = mapping.get(symbol, f"{symbol}.NS")
    yq = Ticker(ticker)
    df = yq.history(period=period)

    if df.empty or 'close' not in df.columns:
        # Fallbacks
        if symbol == "TATAMOTORS": ticker = "TMCV.NS"
        elif symbol == "PEL": ticker = "PIRAMALFIN.NS"
        else: return pd.DataFrame()

        print(f"   [*] Retrying with fallback: {ticker}")
        yq = Ticker(ticker)
        df = yq.history(period=period)

    if df.empty or 'close' not in df.columns: return pd.DataFrame()
    if isinstance(df.index, pd.MultiIndex): df = df.reset_index(level=0, drop=True)
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    return df

async def remediate():
    symbols = ["GUJGASLTD", "LTIM", "PEL", "TATAMOTORS", "ZOMATO", "GMRINFRA", "L&TFH"]
    repo = container.repository
    data_repo = container.data_platform_repo
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)

    print("--- TRADEMIND AI DATA REMEDIATION V7 (fixed) ---")

    for symbol in symbols:
        print(f"[*] Processing {symbol}...")
        try:
            df = await fetch_history_robust(symbol)
            if not df.empty:
                count = 0
                for index, row in df.iterrows():
                    date_str = index.strftime('%Y-%m-%d 00:00:00')
                    exists = conn.execute("SELECT id FROM historical_prices WHERE symbol=? AND date=?", (symbol, date_str)).fetchone()
                    if not exists:
                        conn.execute("INSERT INTO historical_prices (symbol, date, open, high, low, close, volume, source) "
                                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                   (symbol, date_str, float(row['Open']), float(row['High']),
                                    float(row['Low']), float(row['Close']), int(row['Volume']), "remediation"))
                        count += 1
                conn.commit()
                print(f"   [DB] Inserted {count} new price records.")

            # Generate Features with Targets
            prices = await repo.get_recent_prices(symbol, limit=3000)
            if len(prices) < 50: # Minimum for indicators
                print(f"   [FAIL] Insufficient data ({len(prices)} bars)")
                continue

            df_full = pd.DataFrame([p.model_dump() for p in prices])
            df_full.set_index('date', inplace=True)
            df_full.columns = [c.capitalize() for c in df_full.columns]
            df_ta = TechnicalAnalysis.calculate_indicators(df_full)

            # Labeling
            df_ta['target_return'] = df_ta['Close'].shift(-5) / df_ta['Close'] - 1
            df_ta['target'] = (df_ta['target_return'] > 0).astype(float)

            print(f"   [*] Generating features for {len(df_ta)} bars...")
            feat_df = pd.DataFrame(index=df_ta.index)
            feat_df['date'] = df_ta.index
            feat_df['trend_ema_cross'] = (df_ta.get('EMA_20', df_ta['Close']) > df_ta.get('EMA_50', df_ta['Close'])).astype(float)
            feat_df['ema_200'] = df_ta.get('EMA_200', df_ta['Close']).fillna(df_ta['Close'])
            feat_df['sma_20'] = df_ta.get('SMA_20', df_ta['Close']).fillna(df_ta['Close'])
            feat_df['momentum_rsi'] = df_ta.get('RSI', pd.Series(50.0, index=df_ta.index)) / 100.0
            bbl = df_ta.get('BBL', df_ta['Close'] * 0.95)
            bbu = df_ta.get('BBU', df_ta['Close'] * 1.05)
            feat_df['volatility_bb'] = (df_ta['Close'] - bbl) / (bbu - bbl + 1e-9)
            feat_df['volume_relative'] = df_ta['Volume'] / df_ta['Volume'].rolling(20).mean().fillna(df_ta['Volume'])
            feat_df['smc_bullish_ob'] = 0.0
            feat_df['smc_bearish_ob'] = 0.0
            feat_df['ict_liquidity_void'] = ((df_ta['High'] < df_ta['Low'].shift(2)) | (df_ta['Low'] > df_ta['High'].shift(2))).astype(float)
            atr = df_ta.get('ATR', df_ta['Close'] * 0.02)
            feat_df['market_volatility_z'] = (atr - atr.rolling(50).mean()) / (atr.rolling(50).std() + 1e-9)
            feat_df['market_cap_class'] = 2.0
            feat_df['target'] = df_ta['target']

            feat_df = feat_df.fillna(0.0)
            feat_df.dropna(subset=['target'], inplace=True)

            if not feat_df.empty:
                # OVERWRITE Parquet to clean up old NaNs
                parquet_path = Path(f"backend/data/features/{symbol}.parquet")
                if parquet_path.exists():
                    os.remove(parquet_path)

                data_repo.duck.ingest_features(symbol, feat_df)
                print(f"   [SUCCESS] Remediated {symbol} ({len(feat_df)} features)")

        except Exception as e:
            print(f"   [ERROR] {symbol}: {e}")

    conn.close()

if __name__ == "__main__":
    asyncio.run(remediate())
