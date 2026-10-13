"""
NSE Pre-Open Session Order Book Imbalance Scraper & Calculator (09:00 - 09:08 IST)
Calculates equilibrium price (EP) and pre-open buying/selling pressure.
"""

from typing import Dict, Any

class NSEPreOpenAnalyzer:
    @staticmethod
    def evaluate_preopen_imbalance(total_buy_qty: float, total_sell_qty: float, prev_close: float, equilibrium_price: float) -> Dict[str, Any]:
        """
        Evaluates pre-open market session order book imbalance.
        """
        total_qty = total_buy_qty + total_sell_qty
        if total_qty == 0:
            return {"imbalance_ratio": 0.0, "gap_pct": 0.0, "strong_opening": False}

        imbalance_ratio = (total_buy_qty - total_sell_qty) / total_qty
        gap_pct = (equilibrium_price - prev_close) / prev_close if prev_close > 0 else 0.0

        strong_opening = bool(abs(imbalance_ratio) > 0.4 and abs(gap_pct) > 0.005)

        return {
            "imbalance_ratio": imbalance_ratio,
            "gap_pct": gap_pct,
            "equilibrium_price": equilibrium_price,
            "strong_opening": strong_opening
        }
