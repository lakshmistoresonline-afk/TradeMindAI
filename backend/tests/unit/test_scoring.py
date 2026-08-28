import pytest
from backend.services.scoring_service import ScoringService

def test_calculate_unified_score_bullish():
    features = {"trend_ema_cross": 1.0, "momentum_rsi": 0.65}
    ml_prediction = {"prediction": "UP", "confidence": 85.0}
    analysis = {"consensus": "STRONG BUY"}

    result = ScoringService.calculate_unified_score(features, ml_prediction, analysis)

    assert result["score"] > 60
    assert result["grade"] in ["AAA", "AA", "A"]
    assert result["health"]["Technical"] == "GOOD"

def test_calculate_unified_score_bearish():
    features = {"trend_ema_cross": 0.0, "momentum_rsi": 0.35}
    ml_prediction = {"prediction": "DOWN", "confidence": 75.0}
    analysis = {"consensus": "SELL"}

    result = ScoringService.calculate_unified_score(features, ml_prediction, analysis)

    assert result["score"] < 50
    assert result["grade"] in ["C", "D"]
