"""
================================================================================
TradeMindAI: Versioned Research Scorer (v2.3-RESEARCH)
================================================================================
Independent research scorer combining trend, momentum, volume confirmation,
volatility, and relative strength into an explainable heuristic composite score.
Enforces Policy A (Strict Complete-Feature Contract): returns UNAVAILABLE if any
required feature is missing, None, NaN, Inf, string, boolean, or outside valid numeric domains.
Strictly separates heuristic ranking score from calibrated probability (calibrated_probability: None).
Isolated from frozen V2.2 production outputs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class ResearchScorer:
    VERSION = "v2.3-RESEARCH"

    REQUIRED_FEATURES = [
        "Close", "ema_20", "ema_50", "ema_200",
        "res_ema_slope_5", "momentum_rsi", "res_adx_14",
        "res_rel_vol_20", "res_mfi_14", "res_natr",
        "res_rs_20d", "res_donchian_high_20"
    ]

    @staticmethod
    def evaluate_research_signal(row: pd.Series) -> Dict[str, Any]:
        """
        Evaluates a single feature row using research scoring weights under Policy A (Strict Complete-Feature Contract).
        Returns composite heuristic score (0-100), explicit calibrated_probability: None,
        and component sub-scores. Fails closed (status UNAVAILABLE) if any required feature is missing, invalid,
        boolean, non-finite, or outside valid numeric domains.
        """
        for k in ResearchScorer.REQUIRED_FEATURES:
            val = row.get(k)
            # Explicitly reject Python and NumPy booleans
            if val is None or isinstance(val, (str, bool)) or isinstance(val, np.bool_):
                return {
                    "version": ResearchScorer.VERSION,
                    "status": "UNAVAILABLE",
                    "reason": f"Missing, boolean, or invalid type for required feature: {k} (value: {val})",
                    "composite_score": None,
                    "calibrated_probability": None,
                    "heuristic_confidence": None,
                    "sub_scores": {}
                }
            try:
                fval = float(val)
                if not np.isfinite(fval):
                    return {
                        "version": ResearchScorer.VERSION,
                        "status": "UNAVAILABLE",
                        "reason": f"Non-finite value for required feature: {k} (value: {val})",
                        "composite_score": None,
                        "calibrated_probability": None,
                        "heuristic_confidence": None,
                        "sub_scores": {}
                    }

                # Domain validation
                if k in ["Close", "ema_20", "ema_50", "ema_200", "res_donchian_high_20"] and fval <= 0:
                    return {
                        "version": ResearchScorer.VERSION,
                        "status": "UNAVAILABLE",
                        "reason": f"Price/EMA feature {k} must be positive, got {fval}",
                        "composite_score": None,
                        "calibrated_probability": None,
                        "heuristic_confidence": None,
                        "sub_scores": {}
                    }
                if k in ["momentum_rsi", "res_mfi_14"] and not (0.0 <= fval <= 100.0):
                    return {
                        "version": ResearchScorer.VERSION,
                        "status": "UNAVAILABLE",
                        "reason": f"Oscillator feature {k} must be within [0, 100], got {fval}",
                        "composite_score": None,
                        "calibrated_probability": None,
                        "heuristic_confidence": None,
                        "sub_scores": {}
                    }
                if k == "res_adx_14" and not (0.0 <= fval <= 100.0):
                    return {
                        "version": ResearchScorer.VERSION,
                        "status": "UNAVAILABLE",
                        "reason": f"ADX feature {k} must be within [0, 100], got {fval}",
                        "composite_score": None,
                        "calibrated_probability": None,
                        "heuristic_confidence": None,
                        "sub_scores": {}
                    }
                if k in ["res_natr", "res_rel_vol_20"] and fval < 0.0:
                    return {
                        "version": ResearchScorer.VERSION,
                        "status": "UNAVAILABLE",
                        "reason": f"Feature {k} cannot be negative, got {fval}",
                        "composite_score": None,
                        "calibrated_probability": None,
                        "heuristic_confidence": None,
                        "sub_scores": {}
                    }

            except (ValueError, TypeError):
                return {
                    "version": ResearchScorer.VERSION,
                    "status": "UNAVAILABLE",
                    "reason": f"Non-numeric value for required feature: {k} (value: {val})",
                    "composite_score": None,
                    "calibrated_probability": None,
                    "heuristic_confidence": None,
                    "sub_scores": {}
                }

        score_trend = 0.0
        score_momentum = 0.0
        score_volume = 0.0
        score_volatility = 0.0
        score_structure = 0.0

        # 1. Trend (Weight: 25%)
        ema_20 = float(row.get("ema_20", 0))
        ema_50 = float(row.get("ema_50", 0))
        ema_200 = float(row.get("ema_200", 0))
        close = float(row.get("Close", 0))

        if close > ema_20 > ema_50:
            score_trend += 50.0
        if ema_200 > 0 and close > ema_200:
            score_trend += 30.0
        if float(row.get("res_ema_slope_5", 0)) > 0:
            score_trend += 20.0

        score_trend = min(100.0, max(0.0, score_trend))

        # 2. Momentum (Weight: 20%)
        rsi = float(row.get("momentum_rsi", 50))
        adx = float(row.get("res_adx_14", 20))

        if 40 <= rsi <= 65:
            score_momentum += 60.0
        elif 30 <= rsi < 40 or 65 < rsi <= 75:
            score_momentum += 40.0

        if adx >= 20:
            score_momentum += 40.0

        score_momentum = min(100.0, max(0.0, score_momentum))

        # 3. Volume Confirmation (Weight: 25%)
        rel_vol = float(row.get("res_rel_vol_20", 1.0))
        mfi = float(row.get("res_mfi_14", 50))

        if rel_vol >= 1.2:
            score_volume += 50.0
        elif rel_vol >= 1.0:
            score_volume += 30.0

        if 40 <= mfi <= 70:
            score_volume += 50.0

        score_volume = min(100.0, max(0.0, score_volume))

        # 4. Volatility & Risk Suitability (Weight: 15%)
        natr = float(row.get("res_natr", 2.0))
        if natr >= 0:
            if 1.0 <= natr <= 4.0:
                score_volatility += 100.0
            elif natr < 1.0 or natr <= 6.0:
                score_volatility += 60.0

        score_volatility = min(100.0, max(0.0, score_volatility))

        # 5. Price Structure & Relative Strength (Weight: 15%)
        rs_20 = float(row.get("res_rs_20d", 0.0))
        if rs_20 > 0:
            score_structure += 60.0

        donchian_high = float(row.get("res_donchian_high_20", close))
        if close >= donchian_high:
            score_structure += 40.0

        score_structure = min(100.0, max(0.0, score_structure))

        # Composite Heuristic Score (weighted ranking score, NOT probability)
        composite = (
            0.25 * score_trend +
            0.20 * score_momentum +
            0.25 * score_volume +
            0.15 * score_volatility +
            0.15 * score_structure
        )

        return {
            "version": ResearchScorer.VERSION,
            "status": "AVAILABLE",
            "composite_score": round(composite, 2),
            "calibrated_probability": None,  # Explicitly None until rigorous out-of-sample calibration model is fitted
            "heuristic_confidence": round(composite, 2),  # Labeled explicitly as heuristic score, never probability
            "sub_scores": {
                "trend": round(score_trend, 2),
                "momentum": round(score_momentum, 2),
                "volume": round(score_volume, 2),
                "volatility": round(score_volatility, 2),
                "structure": round(score_structure, 2)
            }
        }
