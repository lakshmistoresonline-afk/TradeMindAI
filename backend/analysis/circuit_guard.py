"""
NSE Circuit Limit & Liquidity Proximity Guard
Calculates distance to daily upper/lower price bands (2%, 5%, 10%, 20%) to prevent execution traps.
"""

from typing import Dict, Any

class CircuitGuard:
    @staticmethod
    def evaluate_circuit_proximity(current_price: float, upper_circuit: float, lower_circuit: float, threshold_pct: float = 0.015) -> Dict[str, Any]:
        """
        Blocks trades if current price is within threshold_pct (default 1.5%) of circuit limits.
        """
        if upper_circuit <= 0 or lower_circuit <= 0:
            return {"near_circuit": False, "circuit_type": "NONE"}

        distance_to_upper = (upper_circuit - current_price) / current_price
        distance_to_lower = (current_price - lower_circuit) / current_price

        near_upper = distance_to_upper <= threshold_pct
        near_lower = distance_to_lower <= threshold_pct

        near_circuit = bool(near_upper or near_lower)
        circuit_type = "UPPER" if near_upper else ("LOWER" if near_lower else "NONE")

        return {
            "near_circuit": near_circuit,
            "circuit_type": circuit_type,
            "distance_to_upper_pct": distance_to_upper,
            "distance_to_lower_pct": distance_to_lower
        }
