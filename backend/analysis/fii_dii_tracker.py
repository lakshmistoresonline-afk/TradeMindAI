"""
Daily FII/DII Institutional Flow & Participant OI Tracker
Ingests daily NSE institutional net buy/sell data and index futures participant OI.
"""

from typing import Dict, Any

class FIIDIITracker:
    @staticmethod
    def evaluate_institutional_flows(fii_net_cash_cr: float, dii_net_cash_cr: float, fii_index_futures_long_ratio: float) -> Dict[str, Any]:
        """
        Evaluates institutional participation sentiment.
        """
        is_bullish_institutional = bool(fii_net_cash_cr > 0 and dii_net_cash_cr > -500 and fii_index_futures_long_ratio > 0.55)
        is_bearish_institutional = bool(fii_net_cash_cr < -1000 and fii_index_futures_long_ratio < 0.40)

        sentiment = "NEUTRAL"
        if is_bullish_institutional:
            sentiment = "BULLISH_INSTITUTIONAL"
        elif is_bearish_institutional:
            sentiment = "BEARISH_INSTITUTIONAL"

        return {
            "fii_net_cash_cr": fii_net_cash_cr,
            "dii_net_cash_cr": dii_net_cash_cr,
            "fii_index_futures_long_ratio": fii_index_futures_long_ratio,
            "institutional_sentiment": sentiment,
            "allow_long": not is_bearish_institutional
        }
