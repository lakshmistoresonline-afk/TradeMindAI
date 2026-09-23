"""
================================================================================
TradeMindAI: Local Signal Engine
================================================================================
Evaluates local technical indicators + stored sentiment scores to issue signals:
STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL with confidence ratings and key drivers.
"""

import logging
import pandas as pd
from typing import Dict, Any
from backend.app.services.indicator_service import LocalIndicatorService
from backend.app.services.sentiment_service import LocalSentimentService

logger = logging.getLogger(__name__)

class SignalEngine:
    """
    Evaluates local market metrics and sentiment to issue AI trading signals.
    """

    @staticmethod
    def generate_signal(df_market: pd.DataFrame, news_text: str = "") -> Dict[str, Any]:
        """
        Processes price candles and optional local news text to generate an offline AI trading signal.
        """
        if df_market.empty or len(df_market) < 14:
            return {
                "signal_type": "HOLD",
                "confidence": 50.0,
                "sentiment_score": 0.50,
                "drivers": ["Insufficient historical price data in local database."],
                "metrics": {}
            }

        # 1. Compute Local Technical Indicators
        metrics = LocalIndicatorService.get_latest_metrics(df_market)
        rsi = metrics.get("rsi_14", 50.0)
        macd_hist = metrics.get("macd_hist", 0.0)
        close = metrics.get("close", 0.0)
        ema_20 = metrics.get("ema_20", close)
        ema_50 = metrics.get("ema_50", close)
        ema_200 = metrics.get("ema_200", close)
        bb_upper = metrics.get("bb_upper", close)
        bb_lower = metrics.get("bb_lower", close)

        # 2. Compute Offline Sentiment Score
        sentiment_res = LocalSentimentService.analyze_text(news_text)
        sent_label = sentiment_res["label"]
        sent_score = sentiment_res["score"]

        # 3. Composite Quantitative Signal Logic
        bullish_points = 0
        bearish_points = 0
        drivers = []

        # RSI Logic
        if rsi < 35.0:
            bullish_points += 2
            drivers.append(f"RSI is oversold ({rsi:.1f}), indicating potential bullish reversal.")
        elif rsi > 68.0:
            bearish_points += 2
            drivers.append(f"RSI is overbought ({rsi:.1f}), indicating potential bearish pullback.")

        # MACD Logic
        if macd_hist > 0:
            bullish_points += 1.5
            drivers.append("MACD histogram is positive, confirming upward momentum.")
        else:
            bearish_points += 1.5
            drivers.append("MACD histogram is negative, confirming downward momentum.")

        # EMA Trend Structure
        if close > ema_20 and ema_20 > ema_50:
            bullish_points += 2
            drivers.append("Price is trading above 20 EMA and 50 EMA in bullish alignment.")
        elif close < ema_20 and ema_20 < ema_50:
            bearish_points += 2
            drivers.append("Price is trading below 20 EMA and 50 EMA in bearish alignment.")

        if close > ema_200 and ema_200 > 0:
            bullish_points += 1
            drivers.append("Price is trading above 200 EMA long-term trendline.")

        # Sentiment Boost
        if sent_label == "BULLISH":
            bullish_points += 1.5
            drivers.append(f"Local Sentiment is Bullish ({sent_score*100:.0f}% confidence).")
        elif sent_label == "BEARISH":
            bearish_points += 1.5
            drivers.append(f"Local Sentiment is Bearish ({sent_score*100:.0f}% confidence).")

        # 4. Final Classification
        net_score = bullish_points - bearish_points

        if net_score >= 4.0:
            signal_type = "STRONG_BUY"
            confidence = min(95.0, 75.0 + net_score * 3.5)
        elif net_score >= 1.5:
            signal_type = "BUY"
            confidence = min(85.0, 65.0 + net_score * 4.0)
        elif net_score <= -4.0:
            signal_type = "STRONG_SELL"
            confidence = min(95.0, 75.0 + abs(net_score) * 3.5)
        elif net_score <= -1.5:
            signal_type = "SELL"
            confidence = min(85.0, 65.0 + abs(net_score) * 4.0)
        else:
            signal_type = "HOLD"
            confidence = 60.0

        return {
            "signal_type": signal_type,
            "confidence": round(confidence, 1),
            "sentiment_score": sent_score,
            "drivers": drivers if drivers else ["Price consolidating near key moving averages."],
            "metrics": metrics
        }
