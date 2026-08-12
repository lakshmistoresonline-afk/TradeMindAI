from typing import Any

class SMCAnalysis:
    @staticmethod
    def detect_order_blocks(df: Any):
        """
        SMC v2.0: Structure-Aware Order Block Detection.
        Identifies institutional 'Buy to Sell' or 'Sell to Buy' zones.
        """
        if df is None or len(df) < 10:
            return []

        order_blocks = []
        try:
            # 1. Find swings for structure mapping
            for i in range(5, len(df) - 5):
                # Bullish OB (Last down candle before a displacement up)
                if df["Close"].iloc[i] > df["High"].iloc[i-1:i].max() * 1.01:
                    # Check if previous candle was bearish
                    if df["Close"].iloc[i-1] < df["Open"].iloc[i-1]:
                        order_blocks.append({
                            "type": "bullish",
                            "price": float(df["Low"].iloc[i-1]),
                            "strength": "HIGH",
                            "index": int(i-1)
                        })

                # Bearish OB (Last up candle before a displacement down)
                elif df["Close"].iloc[i] < df["Low"].iloc[i-1:i].min() * 0.99:
                    if df["Close"].iloc[i-1] > df["Open"].iloc[i-1]:
                        order_blocks.append({
                            "type": "bearish",
                            "price": float(df["High"].iloc[i-1]),
                            "strength": "HIGH",
                            "index": int(i-1)
                        })
        except: pass
        return order_blocks

    @staticmethod
    def detect_structure_change(df: Any):
        """
        SMC v2.0: Market Structure Mapping (BOS/CHoCH).
        Detects Break of Structure and Change of Character.
        """
        if df is None or len(df) < 20:
            return {"type": "NONE", "level": 0.0}

        try:
            last_high = df["High"].tail(20).max()
            last_low = df["Low"].tail(20).min()
            current_close = df["Close"].iloc[-1]

            # Break of Structure (BOS) - Trend Continuation
            if current_close > last_high:
                return {"type": "BOS", "bias": "BULLISH", "level": float(last_high)}
            if current_close < last_low:
                return {"type": "BOS", "bias": "BEARISH", "level": float(last_low)}

            # Change of Character (CHoCH) - Trend Reversal Detection
            # (Simplified: Close breaking internal swings)
            return {"type": "IDM", "bias": "NEUTRAL", "level": 0.0} # Inducement
        except: return {"type": "NONE", "level": 0.0}

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
