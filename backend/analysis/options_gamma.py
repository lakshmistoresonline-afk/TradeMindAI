"""
Options Gamma & Put/Call Ratio (PCR) Analytics
Analyzes option chain sentiment, PCR velocity, and gamma exposure walls.
"""

import math
from typing import Dict, Any

class OptionsGammaAnalyzer:
    @staticmethod
    def evaluate_option_chain(pcr: float, iv_skew: float, max_pain: float, spot_price: float) -> Dict[str, Any]:
        """
        Evaluates options derivative data to filter out trap breakouts and gamma squeezes.
        - pcr: Put/Call Ratio (normal range 0.7 to 1.3)
        - iv_skew: Implied volatility skew (call IV vs put IV)
        - max_pain: Strike price with maximum options pain
        """
        # PCR extreme filters
        is_pcr_bullish_trap = pcr > 1.4  # Extreme put buying (bearish sentiment trap)
        is_pcr_bearish_trap = pcr < 0.6  # Extreme call euphoria

        # Gamma wall proximity (distance to max pain)
        distance_to_max_pain_pct = (spot_price - max_pain) / spot_price if max_pain > 0 else 0.0

        # Gamma squeeze potential
        gamma_squeeze_risk = bool(iv_skew < -0.05 and abs(distance_to_max_pain_pct) < 0.01)

        # Signal score adjustment (-1.0 to +1.0)
        sentiment_score = 0.5
        if 0.8 <= pcr <= 1.2:
            sentiment_score = 0.8
        elif is_pcr_bullish_trap or is_pcr_bearish_trap:
            sentiment_score = 0.3

        return {
            "pcr": pcr,
            "iv_skew": iv_skew,
            "max_pain": max_pain,
            "distance_to_max_pain_pct": distance_to_max_pain_pct,
            "gamma_squeeze_risk": gamma_squeeze_risk,
            "sentiment_score": sentiment_score
        }
