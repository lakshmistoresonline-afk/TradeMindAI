from typing import Any

class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(df: Any):
        import pandas as pd
        try:
            import pandas_ta as ta
            HAS_PANDAS_TA = True
        except ImportError:
            import ta
            HAS_PANDAS_TA = False

        if df is None or len(df) < 2:
            return df

        # Institutional Column Normalization
        df.columns = [c.capitalize() for c in df.columns]

        # Ensure required columns exist
        if "Close" not in df.columns:
            return df

        # Trend Indicators (Only most critical to save RAM)
        if HAS_PANDAS_TA:
            import pandas_ta as pta
            df["EMA_20"] = pta.ema(df["Close"], length=20)
            df["EMA_50"] = pta.ema(df["Close"], length=50)
            df["EMA_200"] = pta.ema(df["Close"], length=200)
            df["RSI"] = pta.rsi(df["Close"], length=14)
            df["ATR"] = pta.atr(df["High"], df["Low"], df["Close"], length=14)
            try:
                bbands = pta.bbands(df["Close"])
                if bbands is not None:
                    df["BBL"] = bbands.iloc[:, 0]
                    df["BBU"] = bbands.iloc[:, 2]
            except: pass
        else:
            import ta as talib
            df["EMA_20"] = talib.trend.ema_indicator(df["Close"], window=20)
            df["EMA_50"] = talib.trend.ema_indicator(df["Close"], window=50)
            df["EMA_200"] = talib.trend.ema_indicator(df["Close"], window=200)
            df["RSI"] = talib.momentum.rsi(df["Close"], window=14)
            df["ATR"] = talib.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=14)
            try:
                bb = talib.volatility.BollingerBands(df["Close"])
                df["BBL"] = bb.bollinger_lband()
                df["BBU"] = bb.bollinger_hband()
            except: pass

        # Support & Resistance (Classic Pivots)
        try:
            last_h = df["High"].iloc[-2]
            last_l = df["Low"].iloc[-2]
            last_c = df["Close"].iloc[-2]

            pivot = (last_h + last_l + last_c) / 3
            df["Pivot"] = pivot
        except:
            pass

        return df

    @staticmethod
    def detect_patterns(df: Any):
        return None # Pattern detection disabled to stay under 512MB RAM

    @staticmethod
    def calculate_volume_profile(df: Any, bins=20):
        return {} # Disabled to stay under 512MB RAM
