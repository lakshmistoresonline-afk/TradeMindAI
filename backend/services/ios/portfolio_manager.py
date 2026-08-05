from typing import List, Dict, Any
from backend.domain.models.stock import Stock
from backend.domain.models.data_platform import PortfolioHealth
from backend.services.portfolio_engine import PortfolioEngine

class AIPortfolioManager(PortfolioEngine):
    @staticmethod
    def get_rebalancing_suggestions(holdings: List[Stock], market_bias: str) -> List[Dict[str, Any]]:
        """
        Vision 2.0: Active AI Portfolio Rebalancing.
        """
        suggestions = []

        # 1. Sector Allocation Check
        sectors = {}
        for s in holdings:
            sectors[s.sector] = sectors.get(s.sector, 0) + 1

        total = len(holdings)
        for sector, count in sectors.items():
            weight = count / total
            if weight > 0.35: # Sector concentration limit
                suggestions.append({
                    "type": "REBALANCE",
                    "text": f"High concentration in {sector} ({round(weight*100)}%). Suggest diversifying into underweighted sectors.",
                    "priority": "HIGH"
                })

        # 2. Risk Adjustment based on Market Bias
        if market_bias == "BEARISH":
            suggestions.append({
                "type": "RISK",
                "text": "Market bias is Bearish. Increase cash allocation by 10% and add Nifty Put hedges.",
                "priority": "CRITICAL"
            })

        return suggestions
