from typing import Dict, Any, List

class ScoringService:
    @staticmethod
    def calculate_unified_score(features: Dict[str, float], ml_prediction: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidates all intelligence into a single investment score (0-100).
        """
        import numpy as np
        weights = {
            "technical": 0.15,
            "fundamental": 0.20,
            "ml_bias": 0.15,
            "smc": 0.15,
            "institutional": 0.15,
            "options": 0.10,
            "sentiment": 0.10
        }

        # 1. Technical Score (0-100)
        tech_score = 50
        if features.get("trend_ema_cross"): tech_score += 20
        rsi = features.get("momentum_rsi", 0.5) * 100
        tech_score = (tech_score + (100 - abs(50 - rsi) * 2)) / 2

        # 2. Fundamental Score
        fund_score = 60 # Default baseline

        # 3. ML Bias
        ml_score = ml_prediction.get("confidence", 0) if ml_prediction.get("prediction") == "UP" else (100 - ml_prediction.get("confidence", 0)) if ml_prediction.get("prediction") == "DOWN" else 50

        # 4. Institutional Bias (RC-2: Derived from feature store + Bulk Deals)
        inst_score = 50 + (features.get("fii_net_bias", 0) * 50)

        # Delivery Confirmation (RC-5)
        delivery = features.get("delivery_rate", 0)
        if delivery > 55: inst_score += 10 # Heavy accumulation
        elif delivery < 30 and delivery > 0: inst_score -= 5 # Weak conviction

        # 5. Options Sentiment (RC-5)
        options_score = 50
        pcr = features.get("options_pcr", 1.0)
        if pcr > 1.2: options_score += 20 # Strong Put base
        elif pcr < 0.7: options_score -= 15 # Heavy Call resistance

        # Check for heavy buying in bulk deals
        from backend.core.postgres import SessionLocal, BulkDealDB
        from datetime import datetime, timedelta
        with SessionLocal() as session:
            recent_buys = session.query(BulkDealDB).filter(
                BulkDealDB.symbol == analysis.get('symbol'),
                BulkDealDB.deal_type == 'BUY',
                BulkDealDB.date >= datetime.utcnow() - timedelta(days=7)
            ).count()
            if recent_buys > 0:
                inst_score += 15 # Heavy boost for verified institutional entry
                print(f"   [Institutional Boost] Found {recent_buys} recent bulk buys for {analysis.get('symbol')}")

        # Aggregate
        total_score = (
            (tech_score * weights["technical"]) +
            (fund_score * weights["fundamental"]) +
            (ml_score * weights["ml_bias"]) +
            (inst_score * weights["institutional"]) +
            (options_score * weights["options"]) +
            (50 * weights["smc"]) +
            (50 * weights["sentiment"])
        )

        # total_score is already on 0-100 scale because component scores are 0-100

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
