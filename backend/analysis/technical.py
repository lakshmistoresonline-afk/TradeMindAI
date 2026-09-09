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

        # Institutional Column Normalization: Start with Capitalized OHLCV
        df.columns = [c.capitalize() for c in df.columns]

        # Ensure required columns exist
        if "Close" not in df.columns:
            return df

        # Standard Technical Indicators (Lowercase for Model Compatibility)
        if HAS_PANDAS_TA:
            import pandas_ta as pta
            # Trend
            if "ema_20" not in df.columns: df["ema_20"] = pta.ema(df["Close"], length=20)
            if "sma_20" not in df.columns: df["sma_20"] = pta.sma(df["Close"], length=20)
            if "ema_50" not in df.columns: df["ema_50"] = pta.ema(df["Close"], length=50)
            if "ema_200" not in df.columns: df["ema_200"] = pta.ema(df["Close"], length=200)

            # Momentum
            if "momentum_rsi" not in df.columns: df["momentum_rsi"] = pta.rsi(df["Close"], length=14)

            # Volatility
            if "ATR" not in df.columns: df["ATR"] = pta.atr(df["High"], df["Low"], df["Close"], length=14)
            if "volatility_bb" not in df.columns:
                bbands = pta.bbands(df["Close"])
                if bbands is not None:
                    # (Upper - Lower) / Mid
                    df["volatility_bb"] = (bbands.iloc[:, 2] - bbands.iloc[:, 0]) / bbands.iloc[:, 1]
                else:
                    df["volatility_bb"] = 0.0

            # Crosses
            if "trend_ema_cross" not in df.columns:
                df["trend_ema_cross"] = (df["ema_20"] > df["ema_50"]).astype(int)

            # Volume
            if "volume_sma" not in df.columns: df["volume_sma"] = pta.sma(df["Volume"], length=20)
            if "volume_relative" not in df.columns: df["volume_relative"] = df["Volume"] / df["volume_sma"]

        else:
            import ta as talib
            if "ema_20" not in df.columns: df["ema_20"] = talib.trend.ema_indicator(df["Close"], window=20)
            if "sma_20" not in df.columns: df["sma_20"] = talib.trend.sma_indicator(df["Close"], window=20)
            if "ema_50" not in df.columns: df["ema_50"] = talib.trend.ema_indicator(df["Close"], window=50)
            if "ema_200" not in df.columns: df["ema_200"] = talib.trend.ema_indicator(df["Close"], window=200)

            if "momentum_rsi" not in df.columns: df["momentum_rsi"] = talib.momentum.rsi(df["Close"], window=14)

            if "ATR" not in df.columns: df["ATR"] = talib.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=14)

            if "trend_ema_cross" not in df.columns:
                df["trend_ema_cross"] = (df["ema_20"] > df["ema_50"]).astype(int)

            if "volatility_bb" not in df.columns:
                bb = talib.volatility.BollingerBands(df["Close"])
                df["volatility_bb"] = (bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg()

            if "volume_sma" not in df.columns: df["volume_sma"] = talib.trend.sma_indicator(df["Volume"], window=20)
            if "volume_relative" not in df.columns: df["volume_relative"] = df["Volume"] / df["volume_sma"]

        # Support & Resistance (Classic Pivots)
        try:
            if "Pivot" not in df.columns:
                last_h = df["High"].iloc[-2]
                last_l = df["Low"].iloc[-2]
                last_c = df["Close"].iloc[-2]
                df["Pivot"] = (last_h + last_l + last_c) / 3
        except: pass

        # SMC / ICT Placeholders (satisfy model signature)
        if "smc_bullish_ob" not in df.columns: df["smc_bullish_ob"] = 0
        if "smc_bearish_ob" not in df.columns: df["smc_bearish_ob"] = 0
        if "ict_liquidity_void" not in df.columns: df["ict_liquidity_void"] = 0
        if "market_volatility_z" not in df.columns: df["market_volatility_z"] = 0
        if "market_cap_class" not in df.columns: df["market_cap_class"] = 1 # 1: Large, 2: Mid, 3: Small

        return df

    @staticmethod
    def detect_patterns(df: Any):
        return None

    @staticmethod
    def calculate_volume_profile(df: Any, bins=20):
        return {}
