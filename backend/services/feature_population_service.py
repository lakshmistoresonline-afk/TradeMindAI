"""
================================================================================
TradeMindAI: Technical Feature Population Service (2015 – 2026)
================================================================================
Computes and populates TechnicalFeatureDB for all Nifty 500 stocks from historical
price bars in PriceDB so that SignalEngine.generate_signal() has valid feature inputs.
================================================================================
"""

import os
import sys
import datetime
from datetime import datetime, timezone
from typing import Dict, Any
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.postgres import DATABASE_URL, SessionLocal, StockDB, PriceDB, TechnicalFeatureDB

class FeaturePopulationService:
    """
    Computes technical indicators (EMA, RSI, MACD, ATR) for all stocks
    and populates TechnicalFeatureDB.
    """

    @staticmethod
    def populate_features_for_all_stocks() -> Dict[str, Any]:
        print("[*] Starting Technical Feature Population Service for Nifty 500...")
        engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
        Session = sessionmaker(bind=engine)
        session = Session()

        stocks = session.query(StockDB).all()
        print(f"[*] Processing features for {len(stocks)} stocks...")

        total_features_added = 0

        for idx, stock in enumerate(stocks, 1):
            sym = stock.symbol
            prices = session.query(PriceDB).filter(PriceDB.symbol == sym).order_by(PriceDB.date.asc()).all()
            if len(prices) < 30:
                continue

            df = pd.DataFrame([{
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume
            } for p in prices])

            df['close_s'] = df['close'].astype(float)
            df['sma_20'] = df['close_s'].rolling(window=20).mean()
            df['sma_50'] = df['close_s'].rolling(window=50).mean()
            df['sma_200'] = df['close_s'].rolling(window=200).mean()
            df['ema_20'] = df['close_s'].ewm(span=20, adjust=False).mean()
            df['ema_50'] = df['close_s'].ewm(span=50, adjust=False).mean()
            df['ema_200'] = df['close_s'].ewm(span=200, adjust=False).mean()

            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close_s'].shift())
            low_close = np.abs(df['low'] - df['close_s'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr_14'] = tr.rolling(window=14).mean()

            delta = df['close_s'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-9)
            df['rsi_14'] = 100 - (100 / (1 + rs))

            df = df.fillna(0)

            feature_objects = []
            for _, row in df.iterrows():
                feature_objects.append(TechnicalFeatureDB(
                    symbol=sym,
                    timestamp=row['date'],
                    timeframe="1d",
                    feature_version="v5.6",
                    sma_20=float(row['sma_20']),
                    sma_50=float(row['sma_50']),
                    sma_200=float(row['sma_200']),
                    ema_20=float(row['ema_20']),
                    ema_50=float(row['ema_50']),
                    ema_200=float(row['ema_200']),
                    rsi_14=float(row['rsi_14'] if row['rsi_14'] > 0 else 50.0),
                    atr_14=float(row['atr_14'] if row['atr_14'] > 0 else row['close'] * 0.02)
                ))
                total_features_added += 1

            if feature_objects:
                session.query(TechnicalFeatureDB).filter(TechnicalFeatureDB.symbol == sym).delete()
                session.bulk_save_objects(feature_objects)
                session.commit()

            if idx % 50 == 0 or idx == len(stocks):
                print(f"   [+] Populated TechnicalFeatureDB for {idx}/{len(stocks)} stocks...")

        session.close()
        print(f"[SUCCESS] Feature population complete. Added {total_features_added} feature records.")
        return {"status": "SUCCESS", "features_added": total_features_added}
