import pandas as pd
import numpy as np

class SMCAnalysis:
    @staticmethod
    def detect_order_blocks(df: pd.DataFrame):
        order_blocks = []
        # Simplified OB detection logic:
        # Bullish OB: Last down candle before a strong up move that breaks structure
        # Bearish OB: Last up candle before a strong down move that breaks structure
        for i in range(2, len(df) - 1):
            # Strong move detection (simplified)
            if df["Close"].iloc[i+1] > df["High"].iloc[i] * 1.02: # 2% up move
                if df["Close"].iloc[i] < df["Open"].iloc[i]: # Down candle
                    order_blocks.append({"type": "bullish", "price": df["Close"].iloc[i], "index": i})
        return order_blocks

    @staticmethod
    def detect_fvg(df: pd.DataFrame):
        # Fair Value Gap detection
        fvgs = []
        for i in range(1, len(df) - 1):
            # Bullish FVG: Low of candle 3 is higher than High of candle 1
            if df["Low"].iloc[i+1] > df["High"].iloc[i-1]:
                fvgs.append({"type": "bullish", "top": df["Low"].iloc[i+1], "bottom": df["High"].iloc[i-1], "index": i})
            # Bearish FVG: High of candle 3 is lower than Low of candle 1
            elif df["High"].iloc[i+1] < df["Low"].iloc[i-1]:
                fvgs.append({"type": "bearish", "top": df["Low"].iloc[i-1], "bottom": df["High"].iloc[i+1], "index": i})
        return fvgs
