import pandas as pd
import pandas_ta as ta

class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(df: pd.DataFrame):
        # Trend Indicators
        df["EMA_20"] = ta.ema(df["Close"], length=20)
        df["EMA_50"] = ta.ema(df["Close"], length=50)
        df["EMA_200"] = ta.ema(df["Close"], length=200)

        # Momentum Indicators
        df["RSI"] = ta.rsi(df["Close"], length=14)

        # MACD
        macd = ta.macd(df["Close"])
        df = pd.concat([df, macd], axis=1)

        # Volatility - Bollinger Bands
        bbands = ta.bbands(df["Close"])
        df = pd.concat([df, bbands], axis=1)

        # ADX
        adx = ta.adx(df["High"], df["Low"], df["Close"])
        df = pd.concat([df, adx], axis=1)

        return df

    @staticmethod
    def detect_patterns(df: pd.DataFrame):
        # Candlestick patterns using pandas-ta
        patterns = df.ta.cdl_pattern(name="all")
        return patterns

    @staticmethod
    def calculate_volume_profile(df: pd.DataFrame, bins=20):
        # Calculate Volume at Price
        price_min = df["Low"].min()
        price_max = df["High"].max()
        bin_size = (price_max - price_min) / bins

        # Group volume into price bins
        df["price_bin"] = ((df["Close"] - price_min) // bin_size).clip(0, bins-1)
        profile = df.groupby("price_bin")["Volume"].sum().to_dict()

        return {
            "min": price_min,
            "max": price_max,
            "bin_size": bin_size,
            "profile": profile
        }
