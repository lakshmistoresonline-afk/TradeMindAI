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
            # 1. TREND
            df["ema_20"] = pta.ema(df["Close"], length=20)
            df["sma_20"] = pta.sma(df["Close"], length=20)
            df["ema_50"] = pta.ema(df["Close"], length=50)
            df["ema_100"] = pta.ema(df["Close"], length=100)
            df["ema_200"] = pta.ema(df["Close"], length=200)

            # Slopes (approximate with diff)
            df["ema_20_slope"] = df["ema_20"].diff(5) / 5.0
            df["ema_200_slope"] = df["ema_200"].diff(10) / 10.0

            # 2. MOMENTUM
            df["momentum_rsi"] = pta.rsi(df["Close"], length=14)
            df["momentum_roc"] = pta.roc(df["Close"], length=10)

            macd = pta.macd(df["Close"])
            if macd is not None:
                df["macd"] = macd.iloc[:, 0]
                df["macd_signal"] = macd.iloc[:, 1]
                df["macd_hist"] = macd.iloc[:, 2]

            stoch = pta.stoch(df["High"], df["Low"], df["Close"])
            if stoch is not None:
                df["stoch_k"] = stoch.iloc[:, 0]
                df["stoch_d"] = stoch.iloc[:, 1]

            df["momentum_cci"] = pta.cci(df["High"], df["Low"], df["Close"], length=14)

            adx = pta.adx(df["High"], df["Low"], df["Close"])
            if adx is not None:
                df["adx"] = adx.iloc[:, 0]
                df["dmp"] = adx.iloc[:, 1]
                df["dmn"] = adx.iloc[:, 2]

            # 3. VOLATILITY
            df["ATR"] = pta.atr(df["High"], df["Low"], df["Close"], length=14)
            df["natr"] = (df["ATR"] / df["Close"]) * 100

            bbands = pta.bbands(df["Close"], length=20, std=2.0)
            if bbands is not None:
                df["volatility_bb_width"] = (bbands.iloc[:, 2] - bbands.iloc[:, 0]) / bbands.iloc[:, 1]
                df["volatility_bb_pct"] = (df["Close"] - bbands.iloc[:, 0]) / (bbands.iloc[:, 2] - bbands.iloc[:, 0] + 1e-9)

            # Historical Volatility (20-day)
            df["hist_vol"] = df["Close"].pct_change().rolling(20).std() * (252**0.5) * 100

            # 4. VOLUME
            df["volume_sma"] = pta.sma(df["Volume"], length=20)
            df["volume_relative"] = df["Volume"] / (df["volume_sma"] + 1e-9)
            df["obv"] = pta.obv(df["Close"], df["Volume"])
            df["mfi"] = pta.mfi(df["High"], df["Low"], df["Close"], df["Volume"], length=14)

            # 5. MARKET STRUCTURE (Simplified)
            df["swing_high"] = df["High"].rolling(window=5, center=True).max()
            df["swing_low"] = df["Low"].rolling(window=5, center=True).min()

        else:
            # Fallback to 'ta' library if pandas_ta is missing
            import ta as talib
            df["ema_20"] = talib.trend.ema_indicator(df["Close"], window=20)
            df["sma_20"] = talib.trend.sma_indicator(df["Close"], window=20)
            df["ema_50"] = talib.trend.ema_indicator(df["Close"], window=50)
            df["ema_200"] = talib.trend.ema_indicator(df["Close"], window=200)
            df["momentum_rsi"] = talib.momentum.rsi(df["Close"], window=14)
            df["ATR"] = talib.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=14)
            bb = talib.volatility.BollingerBands(df["Close"])
            df["volatility_bb_width"] = (bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg()
            df["volume_sma"] = talib.trend.sma_indicator(df["Volume"], window=20)
            df["volume_relative"] = df["Volume"] / df["volume_sma"]

        # Crosses
        if "trend_ema_cross" not in df.columns:
            df["trend_ema_cross"] = (df["ema_20"] > df["ema_50"]).astype(float)

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
