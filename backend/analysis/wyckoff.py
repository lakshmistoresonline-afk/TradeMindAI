import pandas as pd

class WyckoffAnalysis:
    @staticmethod
    def detect_phase(df: pd.DataFrame):
        # Extremely simplified Wyckoff phase detection
        # Accumulation: Range bound with increasing volume on up days
        # Distribution: Range bound with increasing volume on down days

        last_50 = df.iloc[-50:]
        price_range = last_50["High"].max() - last_50["Low"].min()
        avg_price = last_50["Close"].mean()

        if price_range / avg_price < 0.1: # Tight range (Accumulation/Distribution candidate)
            # Check volume relationship
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

        return "Unknown"
