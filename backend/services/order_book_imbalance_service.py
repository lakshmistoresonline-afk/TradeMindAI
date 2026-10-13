"""
================================================================================
TradeMindAI: Level-2 Order Book Imbalance (OBI) & Queue Pressure Service
================================================================================
Calculates top-of-book bid/ask queue imbalances to detect institutional resting orders.
"""

from typing import Dict, Any, List

class OrderBookImbalanceService:
    @staticmethod
    def evaluate_obi(bids: List[Dict[str, float]], asks: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Computes Order Book Imbalance (OBI) from top 5 levels of bids and asks.
        """
        if not bids or not asks:
            return {"obi_score": 0.5, "obi_approved": True}

        total_bid_vol = sum(b.get('size', 100.0) for b in bids[:5])
        total_ask_vol = sum(a.get('size', 100.0) for a in asks[:5])

        total_vol = total_bid_vol + total_ask_vol
        obi_score = total_bid_vol / total_vol if total_vol > 0 else 0.5

        approved = bool(obi_score >= 0.55) # Bid pressure dominant

        return {
            "obi_score": round(float(obi_score), 4),
            "obi_approved": approved
        }
