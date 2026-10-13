"""
NSE Expiry Day Max Pain & Gamma Pinning Analytics
Computes option expiry pin risk and Max Pain strike for NIFTY / BANKNIFTY.
"""

from typing import Dict, Any

class ExpiryAnalytics:
    @staticmethod
    def evaluate_expiry_risk(spot_price: float, max_pain_strike: float, is_expiry_day: bool) -> Dict[str, Any]:
        """
        Evaluates spot pinning risk around Max Pain on weekly/monthly expiry days.
        """
        distance_to_max_pain = (spot_price - max_pain_strike) / spot_price if max_pain_strike > 0 else 0.0
        pinning_risk = bool(is_expiry_day and abs(distance_to_max_pain) < 0.005)

        return {
            "max_pain_strike": max_pain_strike,
            "distance_to_max_pain_pct": distance_to_max_pain,
            "is_expiry_day": is_expiry_day,
            "pinning_risk": pinning_risk
        }
