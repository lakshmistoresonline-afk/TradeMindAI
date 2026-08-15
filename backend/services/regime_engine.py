from typing import Dict, Any, Optional
import datetime
import pandas as pd
import numpy as np
from backend.domain.models.ios import MarketRegime

class MarketRegimeEngine:
    @staticmethod
    def detect_regime(index_df: pd.DataFrame, vix_df: pd.DataFrame, breadth_data: Optional[Dict[str, Any]] = None) -> MarketRegime:
        """
        Canonical Regime Detection using Price Trend, Volatility, and Breadth.
        Supports BULL, BEAR, SIDEWAYS, HIGH_VOLATILITY, LOW_VOLATILITY, TRANSITION.
        """
        if index_df.empty:
            return MarketRegime(
                date=datetime.datetime.utcnow(),
                regime="UNKNOWN",
                risk_mode="NEUTRAL",
                sentiment_score=0.5,
                volatility_index=15.0,
                description="Insufficient index data for regime detection."
            )

        # 1. Trend Analysis (EMA 20 vs 50 vs 200)
        close = index_df["Close"]
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        ema200 = close.ewm(span=200, adjust=False).mean()

        last_close = float(close.iloc[-1])
        last_ema20 = float(ema20.iloc[-1])
        last_ema50 = float(ema50.iloc[-1])
        last_ema200 = float(ema200.iloc[-1])

        # Trend Score (0 to 1)
        trend_score = 0.5
        if last_close > last_ema200:
            trend_score += 0.2
            if last_ema20 > last_ema50:
                trend_score += 0.15
            if last_close > last_ema20:
                trend_score += 0.15
        else:
            trend_score -= 0.2
            if last_ema20 < last_ema50:
                trend_score -= 0.15
            if last_close < last_ema20:
                trend_score -= 0.15

        # 2. Volatility Analysis (VIX)
        vix_val = 15.0
        if not vix_df.empty:
            vix_val = float(vix_df["Close"].iloc[-1])

        vol_score = 0.5
        if vix_val > 20: vol_score = 0.8  # High Vol
        elif vix_val < 13: vol_score = 0.2 # Low Vol
        else: vol_score = (vix_val - 10) / 10 # Linear mapping 10-20 -> 0-1

        # 3. Breadth Analysis
        breadth_score = 0.5
        if breadth_data:
            adv = breadth_data.get("advancing", 0)
            dec = breadth_data.get("declining", 0)
            if (adv + dec) > 0:
                breadth_score = adv / (adv + dec)

        # 4. Final Classification
        regime = "SIDEWAYS"
        risk_mode = "NEUTRAL"
        sentiment = (trend_score + breadth_score + (1 - vol_score)) / 3

        if trend_score > 0.7 and vol_score < 0.6:
            regime = "BULL"
            risk_mode = "RISK_ON"
        elif trend_score < 0.3 and vol_score > 0.4:
            regime = "BEAR"
            risk_mode = "RISK_OFF"
        elif vol_score > 0.75:
            regime = "HIGH_VOLATILITY"
            risk_mode = "DELEVERAGE"
        elif abs(trend_score - 0.5) < 0.1 and vol_score < 0.35:
            regime = "LOW_VOLATILITY"
            risk_mode = "ACCUMULATION"
        elif (trend_score > 0.6 and breadth_score < 0.4) or (trend_score < 0.4 and breadth_score > 0.6):
            regime = "TRANSITION"
            risk_mode = "HEDGE"

        description = f"System identified {regime} regime. Trend: {trend_score:.2f}, Volatility: {vix_val:.1f}, Breadth: {breadth_score:.2f}."

        return MarketRegime(
            date=datetime.datetime.utcnow(),
            regime=regime,
            risk_mode=risk_mode,
            sentiment_score=float(sentiment),
            volatility_index=float(vix_val),
            description=description
        )
