from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db.models import MarketData
from backend.core.postgres import TechnicalFeatureDB, Base
from backend.analysis.technical import TechnicalAnalysis

class FeatureCalculationService:
    @staticmethod
    def calculate_and_persist_features(db: Session, symbol: str) -> int:
        """
        Loads historical prices for symbol from MarketData (app_market_data) in trade_mind.db,
        calculates all technical features via TechnicalAnalysis, and persists them into TechnicalFeatureDB.
        Idempotent and PIT-safe. Stores NULL (None) for unavailable values.
        """
        # Ensure TechnicalFeatureDB table exists on db bind
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except:
            pass

        prices = db.query(MarketData).filter(MarketData.symbol == symbol).order_by(MarketData.timestamp.asc()).all()
        if not prices or len(prices) < 20:
            return 0

        df = pd.DataFrame([{
            "Date": p.timestamp,
            "Open": p.open,
            "High": p.high,
            "Low": p.low,
            "Close": p.close,
            "Volume": p.volume
        } for p in prices])

        df.set_index("Date", inplace=True)
        df_ta = TechnicalAnalysis.calculate_indicators(df)

        persisted_count = 0
        for idx, row in df_ta.iterrows():
            if pd.isna(row.get("Close")) or pd.isna(row.get("sma_20")):
                continue

            # Check if feature already exists for (symbol, timestamp)
            existing = db.query(TechnicalFeatureDB).filter(
                TechnicalFeatureDB.symbol == symbol,
                TechnicalFeatureDB.timestamp == idx
            ).first()

            def clean_val(val):
                if pd.isna(val) or val is None or np.isinf(val):
                    return None
                return float(val)

            feat_data = {
                "symbol": symbol,
                "timestamp": idx,
                "timeframe": "1d",
                "feature_version": "v5.6.2",
                "sma_20": clean_val(row.get("sma_20")),
                "sma_50": clean_val(row.get("sma_50")),
                "sma_100": clean_val(row.get("sma_100")),
                "sma_200": clean_val(row.get("sma_200")),
                "ema_20": clean_val(row.get("ema_20")),
                "ema_50": clean_val(row.get("ema_50")),
                "ema_100": clean_val(row.get("ema_100")),
                "ema_200": clean_val(row.get("ema_200")),
                "rsi_14": clean_val(row.get("momentum_rsi")),
                "macd": clean_val(row.get("macd")),
                "macd_signal": clean_val(row.get("macd_signal")),
                "macd_hist": clean_val(row.get("macd_hist")),
                "stoch_k": clean_val(row.get("stoch_k")),
                "stoch_d": clean_val(row.get("stoch_d")),
                "cci": clean_val(row.get("momentum_cci")),
                "adx": clean_val(row.get("adx")),
                "atr_14": clean_val(row.get("ATR")),
                "natr": clean_val(row.get("natr")),
                "historical_volatility": clean_val(row.get("hist_vol")),
                "bb_upper": clean_val(row.get("bb_upper")),
                "bb_middle": clean_val(row.get("sma_20")),
                "bb_lower": clean_val(row.get("bb_lower")),
                "bb_width": clean_val(row.get("volatility_bb_width")),
                "volume_sma": clean_val(row.get("volume_sma")),
                "relative_volume": clean_val(row.get("volume_relative")),
                "obv": clean_val(row.get("obv")),
                "mfi": clean_val(row.get("mfi")),
                "pivot": clean_val((row["High"] + row["Low"] + row["Close"]) / 3.0),
                "calculated_at": datetime.utcnow()
            }

            if existing:
                for k, v in feat_data.items():
                    setattr(existing, k, v)
            else:
                db_feat = TechnicalFeatureDB(**feat_data)
                db.add(db_feat)

            persisted_count += 1

        db.commit()
        return persisted_count
