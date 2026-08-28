from typing import List
import numpy as np

class PortfolioAI:
    @staticmethod
    def calculate_risk(weights: List[float], covariance_matrix: np.ndarray):
        # Portfolio Variance = W' * Cov * W
        portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))
        portfolio_std_dev = np.sqrt(portfolio_variance)
        return portfolio_std_dev

    @staticmethod
    def rebalance_suggestions(current_holdings: dict, target_allocation: dict):
        suggestions = []
        for asset, target_pct in target_allocation.items():
            current_pct = current_holdings.get(asset, 0)
            diff = target_pct - current_pct
            if abs(diff) > 0.05: # 5% threshold
                action = "Buy" if diff > 0 else "Sell"
                suggestions.append({"asset": asset, "action": action, "diff": diff})
        return suggestions
