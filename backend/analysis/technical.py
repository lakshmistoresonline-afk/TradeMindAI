from typing import Any

class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(df: Any):
        import pandas as pd
        import pandas_ta as ta

        if df is None or len(df) < 2:
            return df

        # Institutional Column Normalization
        # Maps any case (close, Close, CLOSE) to the expected TitleCase
        df.columns = [c.capitalize() for c in df.columns]

        # Ensure required columns exist, if not, try to find alternatives
        col_map = {"Volume": ["Vol", "Qty"], "Close": ["Last", "Price"]}
        for target, alts in col_map.items():
            if target not in df.columns:
                for alt in alts:
                    if alt in df.columns:
                        df[target] = df[alt]
                        break

        if "Close" not in df.columns:
            raise KeyError(f"Critical Error: 'Close' column not found in data. Available: {df.columns.tolist()}")

        # Trend Indicators
        df["EMA_20"] = ta.ema(df["Close"], length=20)
        df["EMA_50"] = ta.ema(df["Close"], length=50)
        df["EMA_200"] = ta.ema(df["Close"], length=200)

        # Momentum Indicators
        df["RSI"] = ta.rsi(df["Close"], length=14)

        # MACD
        try:
            macd = ta.macd(df["Close"])
            if macd is not None:
                df = pd.concat([df, macd], axis=1)
        except: pass

        # Volatility - Bollinger Bands
        try:
            bbands = ta.bbands(df["Close"])
            if bbands is not None:
                df = pd.concat([df, bbands], axis=1)
        except: pass

        # ADX
        try:
            adx = ta.adx(df["High"], df["Low"], df["Close"])
            if adx is not None:
                df = pd.concat([df, adx], axis=1)
        except: pass

        # Support & Resistance (Classic Pivots)
        try:
            last_h = df["High"].iloc[-2]
            last_l = df["Low"].iloc[-2]
            last_c = df["Close"].iloc[-2]

            pivot = (last_h + last_l + last_c) / 3
            df["Pivot"] = pivot
            df["R1"] = (2 * pivot) - last_l
            df["S1"] = (2 * pivot) - last_h
            df["R2"] = pivot + (last_h - last_l)
            df["S2"] = pivot - (last_h - last_l)
        except:
            pass

        return df

    @staticmethod
    def detect_patterns(df: Any):
        if df is None or len(df) < 5: return None
        # Candlestick patterns using pandas-ta
        try:
            patterns = df.ta.cdl_pattern(name="all")
            return patterns
        except: return None

    @staticmethod
    def calculate_volume_profile(df: Any, bins=20):
        if df is None or len(df) < bins: return {}
        # Calculate Volume at Price
        try:
            price_min = df["Low"].min()
            price_max = df["High"].max()
            bin_size = (price_max - price_min) / bins

            if bin_size == 0: return {}

            # Group volume into price bins
            df["price_bin"] = ((df["Close"] - price_min) // bin_size).clip(0, bins-1)
            profile = df.groupby("price_bin")["Volume"].sum().to_dict()

            return {
                "min": price_min,
                "max": price_max,
                "bin_size": bin_size,
                "profile": profile
            }
        except: return {}
