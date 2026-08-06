from typing import Dict, Any, List
from backend.domain.interfaces.repository import IMarketDataProvider
import gc

class MultiTimeframeService:
    def __init__(self, provider: IMarketDataProvider):
        self.provider = provider

    async def analyze_alignment(self, symbol: str) -> Dict[str, Any]:
        """
        Vision 2.0: Optimized Multi-Timeframe Bias Alignment.
        Uses tail data to stay under 512MB RAM.
        """
        # 1. Fetch data with optimized periods
        # We only need enough history for SMA (50) and RSI (14)
        df_1h = await self.provider.fetch_history(symbol, period="1mo")
        df_1d = await self.provider.fetch_history(symbol, period="1y") # Reduced from 2y
        df_1w = await self.provider.fetch_history(symbol, period="2y") # Reduced from 5y

        results = {
            "1H": self._get_bias(df_1h, window=20),
            "1D": self._get_bias(df_1d, window=50),
            "1W": self._get_bias(df_1w, window=20)
        }

        # Memory Cleanup
        del df_1h, df_1d, df_1w
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
            close = df["Close"].iloc[-1]
            sma = ta.sma(df["Close"], length=window).iloc[-1]
            rsi = ta.rsi(df["Close"], length=14).iloc[-1]

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
            return {"bias": "NEUTRAL", "score": 50}
