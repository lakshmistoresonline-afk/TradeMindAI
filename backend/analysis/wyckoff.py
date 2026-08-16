from typing import Any

class WyckoffAnalysis:
    @staticmethod
    def detect_phase(df: Any):
        if df is None or len(df) < 5:
            return "Unknown"

        try:
            # Slicing is safe even if len(df) < 50
            last_50 = df.tail(50)

            price_range = last_50["High"].max() - last_50["Low"].min()
            avg_price = last_50["Close"].mean()

            if avg_price == 0: return "Unknown"

            if price_range / avg_price < 0.1: # Tight range
                up_volume = last_50[last_50["Close"] > last_50["Open"]]["Volume"].sum()
                down_volume = last_50[last_50["Close"] < last_50["Open"]]["Volume"].sum()

                if up_volume > down_volume:
                    return "Accumulation"
                else:
                    return "Distribution"

            # Trending phases
            if last_50["Close"].iloc[-1] > last_50["Close"].iloc[0] * 1.1:
                return "Markup"
            elif last_50["Close"].iloc[-1] < last_50["Close"].iloc[0] * 0.9:
                return "Markdown"
        except:
            pass

        return "Unknown"
