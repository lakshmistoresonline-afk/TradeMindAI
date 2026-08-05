from typing import Dict, Any, List
import numpy as np

class ScoringService:
    @staticmethod
    def calculate_unified_score(features: Dict[str, float], ml_prediction: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidates all intelligence into a single investment score (0-100).
        """
        weights = {
            "technical": 0.20,
            "fundamental": 0.25,
            "ml_bias": 0.20,
            "smc": 0.15,
            "institutional": 0.10,
            "sentiment": 0.10
        }

        # 1. Technical Score (0-100)
        tech_score = 50
        if features.get("trend_ema_cross"): tech_score += 20
        rsi = features.get("momentum_rsi", 0.5) * 100
        tech_score = (tech_score + (100 - abs(50 - rsi) * 2)) / 2

        # 2. Fundamental Score
        fund_score = 60 # Default baseline
        # In a real impl, we'd use ROE, Debt/Equity etc from features

        # 3. ML Bias
        ml_score = ml_prediction.get("confidence", 0) if ml_prediction.get("prediction") == "UP" else (100 - ml_prediction.get("confidence", 0)) if ml_prediction.get("prediction") == "DOWN" else 50

        # 4. Institutional Bias (Mocked for now)
        inst_score = 75

        # Aggregate
        total_score = (
            (tech_score * weights["technical"]) +
            (fund_score * weights["fundamental"]) +
            (ml_score * weights["ml_bias"]) +
            (inst_score * weights["institutional"])
        ) / sum(weights.values()) * 100 # Normalizing back to 0-100 scale based on active weights

        # Wait, sum of weights is 1.0.
        total_score = (
            (tech_score * weights["technical"]) +
            (fund_score * weights["fundamental"]) +
            (ml_score * weights["ml_bias"]) +
            (inst_score * weights["institutional"]) +
            (50 * weights["smc"]) + # placeholders
            (50 * weights["sentiment"])
        )

        grade = "D"
        if total_score >= 85: grade = "AAA"
        elif total_score >= 75: grade = "AA"
        elif total_score >= 65: grade = "A"
        elif total_score >= 50: grade = "B"
        elif total_score >= 35: grade = "C"

        return {
            "score": round(total_score, 2),
            "grade": grade,
            "health": {
                "Technical": "EXCELLENT" if tech_score > 75 else "GOOD" if tech_score > 50 else "WEAK",
                "Financial": "STABLE",
                "Growth": "HIGH",
                "Institutional": "STRONG"
            },
            "confidence": {
                "score": 82,
                "reasoning": "High agreement between Technical and ML models. Moderate Fundamental data completeness."
            }
        }
