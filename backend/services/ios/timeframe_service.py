from typing import Dict, Any, List
from backend.domain.interfaces.repository import IMarketDataProvider
import gc

class MultiTimeframeService:
    def __init__(self, provider: IMarketDataProvider):
        self.provider = provider

    async def analyze_alignment(self, symbol: str) -> Dict[str, Any]:
        """
        Vision 2.2: Deep Multi-Timeframe Alignment Matrix.
        Calculates fractal bias from 15m to 1W.
        """
        # 1. Fetch data for all fractal layers
        df_15m = await self.provider.fetch_history(symbol, period="5d", interval="15m")
        df_1h = await self.provider.fetch_history(symbol, period="1mo", interval="1h")
        df_4h = await self.provider.fetch_history(symbol, period="3mo", interval="1h") # 1h is proxy if 4h not supported
        df_1d = await self.provider.fetch_history(symbol, period="1y", interval="1d")
        df_1w = await self.provider.fetch_history(symbol, period="2y", interval="1wk")

        results = {
            "15M": self._get_bias(df_15m, window=20),
            "1H": self._get_bias(df_1h, window=20),
            "4H": self._get_bias(df_4h, window=50),
            "1D": self._get_bias(df_1d, window=50),
            "1W": self._get_bias(df_1w, window=20)
        }

        # Memory Cleanup
        del df_15m, df_1h, df_4h, df_1d, df_1w
        gc.collect()

        # 2. Alignment Logic
        biases = [r["bias"] for r in results.values()]
        alignment = "ALIGNED" if all(b == biases[0] for b in biases) else "CONFLICTED"

        return {
            "timeframes": results,
            "alignment_status": alignment,
            "overall_bias": biases[1],
            "summary": f"Institutional alignment is {alignment}. Primary bias is {biases[1]}."
        }

    def _get_bias(self, df: Any, window: int) -> Dict[str, Any]:
        if df is None or df.empty or len(df) < window:
            return {"bias": "NEUTRAL", "score": 50}

        import pandas_ta as ta
        # Force column standardization
        df.columns = [c.capitalize() for c in df.columns]

        try:
            import math
            close = df["Close"].iloc[-1]
            if math.isnan(close): close = 0.0

            sma = ta.sma(df["Close"], length=window).iloc[-1]
            if math.isnan(sma): sma = close

            rsi = ta.rsi(df["Close"], length=14).iloc[-1]
            if math.isnan(rsi): rsi = 50.0

            bias = "NEUTRAL"
            score = 50

            if close > sma:
                bias = "BULLISH"
                score += 20
            elif close < sma:
                bias = "BEARISH"
                score -= 20

            if rsi > 60: score += 15
            elif rsi < 40: score -= 15

            return {
                "bias": "BULLISH" if score > 60 else "BEARISH" if score < 40 else "NEUTRAL",
                "score": round(score, 2),
                "price": float(close)
            }
        except:
            return {"bias": "NEUTRAL", "score": 50, "price": 0.0}
