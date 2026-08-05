from typing import List, Dict, Any
from backend.domain.models.stock import Stock
from backend.domain.models.data_platform import PortfolioHealth
import pandas as pd
import numpy as np

class PortfolioEngine:
    @staticmethod
    def analyze_health(user_id: str, holdings: List[Stock]) -> PortfolioHealth:
        """
        Calculates aggregate portfolio metrics and health score.
        """
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

        # 3. Risk Level (Based on aggregate Beta - placeholder logic)
        avg_beta = 1.0 # In real impl, fetch from QuantMetrics
        risk_level = "MED"
        if avg_beta < 0.8: risk_level = "LOW"
        elif avg_beta > 1.2: risk_level = "HIGH"

        # 4. Health Score calculation
        health_score = (diversification * 0.4) + (60 if risk_level != "HIGH" else 40)

        return PortfolioHealth(
            user_id=user_id,
            health_score=float(health_score),
            diversification_score=float(diversification),
            risk_level=risk_level,
            sector_allocation=sector_allocation,
            expected_annual_return=12.5, # Mock: use ML prediction weighted avg
            max_drawdown=-15.0
        )
