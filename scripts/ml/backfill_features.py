
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
from backend.analysis.technical import TechnicalAnalysis

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

    # 2. Technical Indicators
    df_ta = TechnicalAnalysis.calculate_indicators(df)

    # 3. Target Generation (Multi-Horizon Support)
    # SHORT: 7 days, SWING: 30 days, LONG: 180 days (approximated candles)
    df_ta['target_short'] = (df_ta['Close'].shift(-7) / df_ta['Close'] - 1 > 0).astype(float)
    df_ta['target_swing'] = (df_ta['Close'].shift(-30) / df_ta['Close'] - 1 > 0).astype(float)
    df_ta['target_long'] = (df_ta['Close'].shift(-180) / df_ta['Close'] - 1 > 0).astype(float)

    # Legacy field
    df_ta['target'] = df_ta['target_swing']

    # 4. Feature Extraction (Optimized Vectorized)
    feat_df = pd.DataFrame(index=df_ta.index)
    feat_df['date'] = df_ta.index
    feat_df['trend_ema_cross'] = (df_ta.get('EMA_20', df_ta['Close']) > df_ta.get('EMA_50', df_ta['Close'])).astype(float)
    feat_df['ema_200'] = df_ta.get('EMA_200', df_ta['Close']).fillna(df_ta['Close'])
    feat_df['sma_20'] = df_ta.get('SMA_20', df_ta['Close']).fillna(df_ta['Close'])
    feat_df['momentum_rsi'] = df_ta.get('RSI', pd.Series(50.0, index=df_ta.index)) / 100.0

    # Handle Bollinger Bands columns
    bbl = df_ta.get('BBL', df_ta['Close'] * 0.95)
    bbu = df_ta.get('BBU', df_ta['Close'] * 1.05)
    feat_df['volatility_bb'] = (df_ta['Close'] - bbl) / (bbu - bbl + 1e-9)

    feat_df['volume_relative'] = df_ta['Volume'] / df_ta['Volume'].rolling(20).mean().fillna(df_ta['Volume'])
    feat_df['Close'] = df_ta['Close'] # Phase 4 Hardening: Carry price for signal generation

    # SMC Logic Approximation (Vectorized for backfill speed)
    feat_df['smc_bullish_ob'] = 0.0
    feat_df.loc[(df_ta['Close'] > df_ta['High'].shift(1) * 1.01) & (df_ta['Close'].shift(1) < df_ta['Open'].shift(1)), 'smc_bullish_ob'] = 1.0

    feat_df['smc_bearish_ob'] = 0.0
    feat_df.loc[(df_ta['Close'] < df_ta['Low'].shift(1) * 0.99) & (df_ta['Close'].shift(1) > df_ta['Open'].shift(1)), 'smc_bearish_ob'] = 1.0

    feat_df['ict_liquidity_void'] = ((df_ta['High'] < df_ta['Low'].shift(2)) | (df_ta['Low'] > df_ta['High'].shift(2))).astype(float)

    # Volatility Z-Score
    atr = df_ta.get('ATR', df_ta['Close'] * 0.02)
    feat_df['market_volatility_z'] = (atr - atr.rolling(50).mean()) / (atr.rolling(50).std() + 1e-9)
    feat_df['market_volatility_z'] = feat_df['market_volatility_z'].fillna(0.0)
    feat_df['ATR'] = atr # Phase 4 Hardening

    feat_df['market_cap_class'] = 2.0
    feat_df['target_short'] = df_ta['target_short']
    feat_df['target_swing'] = df_ta['target_swing']
    feat_df['target_long'] = df_ta['target_long']
    feat_df['target'] = df_ta['target']

    # Final cleanup
    # We keep NaN targets for latest rows to support inference
    # Drop rows where critical price data is missing
    feat_df.dropna(subset=['Close', 'ATR'], inplace=True)

    # Validation
    if feat_df.empty: return

    # 5. Bulk Ingest into DuckDB
    data_repo.duck.ingest_features(symbol, feat_df)

async def run_backfill():
    print("--- OPTIMIZED FEATURE BACKFILL v2 ---")
    with container.repository.session_factory() as pg:
        from backend.core.postgres import StockDB
        symbols = [s.symbol for s in pg.query(StockDB.symbol).all()]

    print(f"[*] Backfilling {len(symbols)} symbols...")
    for symbol in tqdm(symbols):
        try:
            await backfill_symbol(symbol)
        except Exception as e:
            print(f"Error backfilling {symbol}: {e}")

if __name__ == "__main__":
    asyncio.run(run_backfill())
