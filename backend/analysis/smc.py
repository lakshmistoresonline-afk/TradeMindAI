from typing import Any

class SMCAnalysis:
    @staticmethod
    def detect_order_blocks(df: Any):
        if df is None or len(df) < 5:
            return []

        order_blocks = []
        try:
            # TitleCase columns assumed normalized in TechnicalAnalysis
            for i in range(2, len(df) - 1):
                if df["Close"].iloc[i+1] > df["High"].iloc[i] * 1.02: # 2% up move
                    if df["Close"].iloc[i] < df["Open"].iloc[i]: # Down candle
                        order_blocks.append({"type": "bullish", "price": float(df["Close"].iloc[i]), "index": int(i)})
                elif df["Close"].iloc[i+1] < df["Low"].iloc[i] * 0.98: # 2% down move
                    if df["Close"].iloc[i] > df["Open"].iloc[i]: # Up candle
                        order_blocks.append({"type": "bearish", "price": float(df["Close"].iloc[i]), "index": int(i)})
        except:
            pass
        return order_blocks

    @staticmethod
    def detect_fvg(df: Any):
        if df is None or len(df) < 3:
            return []

        fvgs = []
        try:
            for i in range(1, len(df) - 1):
                # Bullish FVG: Low of candle 3 is higher than High of candle 1
                if df["Low"].iloc[i+1] > df["High"].iloc[i-1]:
                    fvgs.append({"type": "bullish", "top": float(df["Low"].iloc[i+1]), "bottom": float(df["High"].iloc[i-1]), "index": int(i)})
                # Bearish FVG: High of candle 3 is lower than Low of candle 1
                elif df["High"].iloc[i+1] < df["Low"].iloc[i-1]:
                    fvgs.append({"type": "bearish", "top": float(df["Low"].iloc[i-1]), "bottom": float(df["High"].iloc[i+1]), "index": int(i)})
        except:
            pass
        return fvgs
