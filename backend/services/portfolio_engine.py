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

    @staticmethod
    def optimize_weights(holdings: List[Stock]) -> Dict[str, float]:
        """
        Vision 2.2: Mean-Variance Optimization (Simplified Markowitz).
        Calculates suggested rebalancing weights to maximize Sharpe Ratio.
        """
        import numpy as np
        if not holdings or len(holdings) < 2:
            return {s.symbol: 100.0/len(holdings) for s in holdings} if holdings else {}

        # 1. Gather expected returns (based on AI scores) and risk (Beta)
        symbols = [s.symbol for s in holdings]
        # Heuristic return: AI Score scaled to 5-25% annual
        expected_returns = np.array([((s.ai_investment_score or 50) / 100) * 0.20 for s in holdings])
        # Risk proxy: Beta
        betas = np.array([s.beta or 1.0 for s in holdings])

        # 2. Simple Inverse-Beta Weighting (Low Beta = High Weight)
        # This is a robust institutional baseline for stability
        inv_betas = 1.0 / betas
        suggested_weights = (inv_betas / np.sum(inv_betas)) * 100

        # 3. Adjust slightly by AI Conviction
        # Top conviction picks get a 10% weight boost
        avg_score = np.mean([s.ai_investment_score or 50 for s in holdings])
        for i, s in enumerate(holdings):
            if (s.ai_investment_score or 0) > avg_score:
                suggested_weights[i] *= 1.1

        # Re-normalize to 100%
        suggested_weights = (suggested_weights / np.sum(suggested_weights)) * 100

        return {symbols[i]: round(float(suggested_weights[i]), 2) for i in range(len(symbols))}
