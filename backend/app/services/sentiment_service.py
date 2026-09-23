"""
================================================================================
TradeMindAI: Local Sentiment Service
================================================================================
Analyzes stored local news text using local Hugging Face FinBERT or local Ollama endpoints.
Falls back gracefully to rule-based keyword sentiment if local ML model is offline.
"""

import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Positive and negative keyword dictionaries for offline rule-based fallback
POSITIVE_KEYWORDS = [
    "profit", "growth", "surge", "gain", "bullish", "revenue", "expansion",
    "outperform", "dividend", "beat", "rally", "record", "robust", "strong"
]

NEGATIVE_KEYWORDS = [
    "loss", "decline", "drop", "bearish", "miss", "plunge", "slash",
    "lawsuit", "investigation", "debt", "default", "weak", "slump", "down"
]

class LocalSentimentService:
    """
    Offline financial sentiment analysis service.
    """

    @staticmethod
    def analyze_text(text_content: str) -> Dict[str, Any]:
        """
        Analyzes financial sentiment using Ollama API -> HuggingFace FinBERT -> Rule-Based Fallback.
        """
        if not text_content or not text_content.strip():
            return {"label": "NEUTRAL", "score": 0.5, "method": "DEFAULT"}

        # Method 1: Local Ollama Endpoint (http://localhost:11434)
        try:
            ollama_resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"Classify the financial sentiment of this news text as BULLISH, BEARISH, or NEUTRAL with a confidence score 0.0-1.0:\n\n{text_content}",
                    "stream": False
                },
                timeout=3
            )
            if ollama_resp.status_code == 200:
                out = ollama_resp.json().get("response", "").upper()
                if "BULLISH" in out:
                    return {"label": "BULLISH", "score": 0.85, "method": "LOCAL_OLLAMA"}
                elif "BEARISH" in out:
                    return {"label": "BEARISH", "score": 0.85, "method": "LOCAL_OLLAMA"}
                elif "NEUTRAL" in out:
                    return {"label": "NEUTRAL", "score": 0.50, "method": "LOCAL_OLLAMA"}
        except Exception:
            logger.debug("[Sentiment] Local Ollama API offline. Testing Hugging Face FinBERT...")

        # Method 2: Local Hugging Face Transformers Pipeline (ProsusAI/finbert)
        try:
            from transformers import pipeline
            finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            res = finbert(text_content[:512])[0]
            label_map = {"positive": "BULLISH", "negative": "BEARISH", "neutral": "NEUTRAL"}
            return {
                "label": label_map.get(res["label"].lower(), "NEUTRAL"),
                "score": round(float(res["score"]), 2),
                "method": "LOCAL_FINBERT"
            }
        except Exception:
            logger.debug("[Sentiment] Local FinBERT offline. Utilizing Rule-Based Keyword Fallback.")

        # Method 3: Rule-Based Keyword Fallback (100% Guaranteed Offline Execution)
        text_lower = text_content.lower()
        pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
        neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)

        if pos_count > neg_count:
            score = round(min(0.95, 0.5 + (pos_count - neg_count) * 0.1), 2)
            return {"label": "BULLISH", "score": score, "method": "RULE_BASED_FALLBACK"}
        elif neg_count > pos_count:
            score = round(min(0.95, 0.5 + (neg_count - pos_count) * 0.1), 2)
            return {"label": "BEARISH", "score": score, "method": "RULE_BASED_FALLBACK"}

        return {"label": "NEUTRAL", "score": 0.5, "method": "RULE_BASED_FALLBACK"}
