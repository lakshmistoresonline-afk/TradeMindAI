from typing import List, Dict, Any
from backend.domain.models.stock import Stock
from backend.domain.models.data_platform import PortfolioHealth

class PortfolioEngine:
    @staticmethod
    def analyze_health(user_id: str, holdings: List[Stock]) -> PortfolioHealth:
        """
        Calculates aggregate portfolio metrics and health score.
        """
        import numpy as np
        if not holdings:
            return PortfolioHealth(
                user_id=user_id, health_score=0, diversification_score=0,
                risk_level="NONE", sector_allocation={},
                expected_annual_return=0, max_drawdown=0
            )

        # 1. Sector Allocation
        sector_counts = {}
        for stock in holdings:
            sector = stock.sector or "Unknown"
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        total = len(holdings)
        sector_allocation = {s: (c/total)*100 for s, c in sector_counts.items()}

        # 2. Diversification Score (Simplified HHI index)
        weights = np.array(list(sector_allocation.values())) / 100
        hhi = np.sum(weights**2)
        diversification = (1 - hhi) * 100 # 100 is perfectly diversified

        # 3. Risk Level (Beta-Weighted)
        valid_betas = [s.beta for s in holdings if s.beta is not None]
        avg_beta = np.mean(valid_betas) if valid_betas else 1.0

        risk_level = "MED"
        if avg_beta < 0.85: risk_level = "LOW"
        elif avg_beta > 1.15: risk_level = "HIGH"

        # 4. Health Score calculation
        # RC-2: Derived metrics from AI scores
        avg_ai_score = np.mean([s.ai_investment_score for s in holdings if s.ai_investment_score]) if holdings else 50
        health_score = (diversification * 0.4) + (avg_ai_score * 0.6)

        return PortfolioHealth(
            user_id=user_id,
            health_score=float(health_score),
            diversification_score=float(diversification),
            risk_level=risk_level,
            sector_allocation=sector_allocation,
            expected_annual_return=float(avg_ai_score * 0.2), # Heuristic: higher score -> higher expected alpha
            max_drawdown=-12.5 # Minimum institutional risk baseline
        )
