"""
================================================================================
TradeMindAI: Local Indicator Service
================================================================================
Computes technical indicators locally across historical price candles:
RSI (14), MACD (12, 26, 9), EMA (20, 50, 200), and Bollinger Bands (20, 2).
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class LocalIndicatorService:
    """
    Computes technical analysis metrics locally in memory.
    """

    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates RSI, MACD, EMAs, and Bollinger Bands on OHLCV dataframe.
        """
        if df.empty or len(df) < 14:
            logger.warning("[Indicators] Insufficient candles for indicator calculation.")
            return df

        df = df.copy()
        close = df["close"]

        # 1. Exponential Moving Averages (EMA 20, 50, 200)
        df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        df["ema_50"] = close.ewm(span=50, adjust=False).mean()
        if len(df) >= 200:
            df["ema_200"] = close.ewm(span=200, adjust=False).mean()
        else:
            df["ema_200"] = np.nan

        # 2. Relative Strength Index (RSI 14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df["rsi_14"] = 100.0 - (100.0 / (1.0 + rs))

        # 3. MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # 4. Bollinger Bands (20, 2) and SMA 20
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        df["bb_upper"] = sma_20 + (std_20 * 2.0)
        df["bb_lower"] = sma_20 - (std_20 * 2.0)
        df["bb_middle"] = sma_20
        df["sma_20"] = sma_20

        # 5. Average True Range (ATR 14)
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            prev_close = close.shift(1)
            tr = pd.concat([
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs()
            ], axis=1).max(axis=1)
            df["atr_14"] = tr.rolling(window=14).mean()

        return df

    @staticmethod
    def get_latest_metrics(df: pd.DataFrame) -> dict:
        """
        Extracts latest indicator values as a clean dictionary.
        """
        df_ta = LocalIndicatorService.calculate_indicators(df)
        if df_ta.empty:
            return {}

        last = df_ta.iloc[-1]
        def _fmt(key):
            val = last.get(key) if hasattr(last, "get") else None
            return round(float(val), 2) if val is not None and pd.notna(val) else None

        return {
            "symbol": str(df_ta.get("symbol", pd.Series([""])).iloc[-1] if "symbol" in df_ta.columns else ""),
            "close": float(last["close"]) if "close" in last and pd.notna(last["close"]) else 0.0,
            "rsi_14": _fmt("rsi_14"),
            "macd": _fmt("macd"),
            "macd_signal": _fmt("macd_signal"),
            "macd_hist": _fmt("macd_hist"),
            "ema_20": _fmt("ema_20"),
            "ema_50": _fmt("ema_50"),
            "ema_200": _fmt("ema_200"),
            "bb_upper": _fmt("bb_upper"),
            "bb_lower": _fmt("bb_lower"),
            "bb_middle": _fmt("bb_middle"),
            "atr_14": _fmt("atr_14")
        }
