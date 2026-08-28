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
        tech_score = features.get("technical_score")
        if tech_score is None:
            # Calculate if missing
            tech_score = 50
            if features.get("trend_ema_cross"): tech_score += 20
            rsi = features.get("momentum_rsi")
            if rsi is not None:
                tech_score = (tech_score + (100 - abs(50 - rsi * 100) * 2)) / 2
            else:
                tech_score = None # DATA_INSUFFICIENT

        # 2. Fundamental Score
        fund_score = features.get("fundamental_quality_score") # None if insufficient

        # 3. ML Bias
        ml_score = None
        if ml_prediction.get("confidence") is not None:
             ml_score = ml_prediction.get("confidence", 0) if ml_prediction.get("prediction") == "UP" else (100 - ml_prediction.get("confidence", 0)) if ml_prediction.get("prediction") == "DOWN" else 50

        # 4. Institutional Bias
        inst_score = None
        fii_bias = features.get("fii_net_bias")
        if fii_bias is not None:
            inst_score = 50 + (fii_bias * 50)

            # Delivery Confirmation (RC-5)
            delivery = features.get("delivery_rate")
            if delivery is not None:
                if delivery > 55: inst_score += 10 # Heavy accumulation
                elif delivery < 30 and delivery > 0: inst_score -= 5 # Weak conviction

        # 5. Options Sentiment (RC-5)
        options_score = features.get("options_sentiment_score")
        pcr = features.get("options_pcr")
        if options_score is not None and pcr is not None:
            if pcr > 1.2: options_score += 20 # Strong Put base
            elif pcr < 0.7: options_score -= 15 # Heavy Call resistance

        # 6. SMC & Sentiment
        smc_score = features.get("smc_alignment_score")
        sentiment_score = features.get("news_sentiment_score")

        # Check for essential components
        if tech_score is None or ml_score is None:
            return {
                "score": 0,
                "grade": "N/A",
                "status": "DATA_INSUFFICIENT",
                "health": {"Technical": "UNKNOWN", "Financial": "UNKNOWN", "Growth": "UNKNOWN", "Institutional": "UNKNOWN"},
                "confidence": {"score": 0, "reasoning": "Insufficient core data for forensic scoring."}
            }

        # Aggregate with missing handling
        total_weight = 0
        weighted_sum = 0

        component_scores = {
            "technical": tech_score,
            "fundamental": fund_score,
            "ml_bias": ml_score,
            "smc": smc_score,
            "institutional": inst_score,
            "options": options_score,
            "sentiment": sentiment_score
        }

        for comp, val in component_scores.items():
            if val is not None:
                weighted_sum += (val * weights[comp])
                total_weight += weights[comp]

        if total_weight == 0: return {"score": 0, "grade": "N/A"}

        total_score = weighted_sum / total_weight

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
                "Technical": "EXCELLENT" if (tech_score or 0) > 75 else "GOOD" if (tech_score or 0) > 50 else "WEAK",
                "Financial": "STABLE" if (fund_score or 0) > 50 else "VOLATILE" if fund_score is not None else "UNKNOWN",
                "Growth": "HIGH" if (fund_score or 0) > 70 else "MODERATE" if fund_score is not None else "UNKNOWN",
                "Institutional": "STRONG" if (inst_score or 50) > 65 else "ACCUMULATING" if (inst_score or 50) > 50 else "DISTRIBUTION" if inst_score is not None else "NEUTRAL"
            },
            "confidence": {
                "score": round(total_score, 0),
                "reasoning": f"Intelligence consolidated across {len([w for w in component_scores if component_scores[w] is not None])} validated vectors."
            }
        }
