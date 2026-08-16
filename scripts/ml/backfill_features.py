import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.domain.models.data_platform import FeatureVector

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def calculate_rsi(series, length=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

async def backfill_symbol(symbol: str):
    repo = container.repository
    data_repo = container.data_platform_repo

    # 1. Fetch all prices
    prices = await repo.get_recent_prices(symbol, limit=5000)
    if not prices: return

    df = pd.DataFrame([p.model_dump() for p in prices])
    df.set_index('date', inplace=True)
    df.columns = [c.capitalize() for c in df.columns]

    if len(df) < 200: return

    # 2. Vectorized Indicator Calculation
    df["EMA_20"] = calculate_ema(df["Close"], 20)
    df["EMA_50"] = calculate_ema(df["Close"], 50)
    df["EMA_200"] = calculate_ema(df["Close"], 200)
    df["RSI"] = calculate_rsi(df["Close"], 14)

    # Simple ATR
    df['high_low'] = df['High'] - df['Low']
    df['high_cp'] = (df['High'] - df['Close'].shift(1)).abs()
    df['low_cp'] = (df['Low'] - df['Close'].shift(1)).abs()
    df['tr'] = df[['high_low', 'high_cp', 'low_cp']].max(axis=1)
    df['ATR'] = df['tr'].rolling(14).mean()

    # Bollinger Bands
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['STD_20'] = df['Close'].rolling(20).std()
    df['BBU'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['BBL'] = df['SMA_20'] - (df['STD_20'] * 2)

    # 3. Target Generation
    df['target_return'] = df['Close'].shift(-5) / df['Close'] - 1
    df['target'] = (df['target_return'] > 0.01).astype(float)

    # 4. Feature Extraction (Vectorized)
    feat_df = pd.DataFrame(index=df.index)
    feat_df['date'] = df.index
    feat_df['trend_ema_cross'] = (df['EMA_20'] > df['EMA_50']).astype(float)
    feat_df['momentum_rsi'] = df['RSI'] / 100.0
    feat_df['volatility_bb'] = (df['Close'] - df['BBL']) / (df['BBU'] - df['BBL'] + 1e-9)
    feat_df['volume_relative'] = df['Volume'] / df['Volume'].rolling(20).mean()
    feat_df['smc_bullish_ob'] = 0.0 # Mocked for P0
    feat_df['smc_bearish_ob'] = 0.0
    feat_df['ict_liquidity_void'] = 0.0
    feat_df['target'] = df['target']

    # Cleanup
    feat_df.dropna(inplace=True)
    if feat_df.empty: return

    # 5. Bulk Ingest into DuckDB
    # Bypass individual save_feature_vector for speed
    data_repo.duck.ingest_features(symbol, feat_df)

async def run_backfill():
    print("============================================================")
    print(" TRADEMIND AI - OPTIMIZED FEATURE BACKFILL")
    print("============================================================")

    with container.repository.session_factory() as pg:
        from backend.core.postgres import StockDB
        symbols = [s.symbol for s in pg.query(StockDB.symbol).filter(StockDB.index_membership == 'NIFTY_200').all()]

    print(f"[*] Backfilling {len(symbols)} symbols...")

    for symbol in tqdm(symbols):
        try:
            await backfill_symbol(symbol)
        except Exception as e:
            print(f"Error backfilling {symbol}: {e}")

if __name__ == "__main__":
    asyncio.run(run_backfill())
