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
        events = SMCAnalysis.detect_structure_change_multi(df)
        if events:
            return events[-1]
        return {"type": "NONE", "level": 0.0}

    @staticmethod
    def detect_structure_change_multi(df: Any) -> list:
        """
        Scans full history for multiple BOS/CHoCH events.
        """
        if df is None or len(df) < 20:
            return []

        events = []
        try:
            # Using a sliding window to detect historical breaks
            for i in range(20, len(df)):
                window = df.iloc[i-20:i]
                high = window["High"].max()
                low = window["Low"].min()
                current = df.iloc[i]

                if current["Close"] > high:
                    events.append({
                        "type": "BOS",
                        "bias": "BULLISH",
                        "level": float(high),
                        "date": current.name,
                        "price": float(current["Close"])
                    })
                elif current["Close"] < low:
                    events.append({
                        "type": "BOS",
                        "bias": "BEARISH",
                        "level": float(low),
                        "date": current.name,
                        "price": float(current["Close"])
                    })

            # Filter to avoid "cluster" signals (only one per 5 days)
            filtered = []
            if events:
                filtered.append(events[0])
                for e in events[1:]:
                    if (e['date'] - filtered[-1]['date']).days > 5:
                        filtered.append(e)
            return filtered
        except:
            return []

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
