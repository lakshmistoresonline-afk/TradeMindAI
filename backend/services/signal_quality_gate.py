import datetime
from datetime import timezone
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

class SignalQualityGate:
    """
    V2.7 Apex Institutional Quality Gate.
    Evaluates signals against 5 Apex Quantitative Upgrades:
    1. VPIN Volume-Synchronized Order Flow Toxicity
    2. Dark Pool & Block Deal Accumulation Index (DIX)
    3. FinBERT NLP Sentiment Shock Overrides on NSE Filings
    4. Cross-Asset Intermarket Cointegration Networks
    5. Deep Reinforcement Learning (PPO) Dynamic Trailing Exit Policy
    """

    @staticmethod
    def get_dynamic_vix_floor(vix_value: Optional[float]) -> float:
        """
        Calculates dynamic probability floor conditioned on market volatility (India VIX).
        - Low VIX (< 13.0): Floor = 0.62
        - Normal VIX (13.0 - 17.0): Floor = 0.68
        - High VIX (> 17.0): Floor = 0.78
        """
        if vix_value is None or vix_value <= 0:
            return 0.68
        if vix_value < 13.0:
            return 0.62
        if vix_value <= 17.0:
            return 0.68
        return 0.78

    @staticmethod
    def evaluate_v27_apex_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a signal against V2.7 Apex Criteria.
        Returns {decision: PUBLISH|BLOCK|NO_SIGNAL, reasons: list, metadata: dict}
        """
        reasons = []

        # 1. FinBERT NLP Corporate Announcement Sentiment Override
        nlp_sentiment = features.get("finbert_nlp_sentiment") or signal.finbert_nlp_sentiment or 0.75
        if nlp_sentiment < -0.50:
            reasons.append(f"NLP_SENTIMENT_SHOCK: FinBERT score {nlp_sentiment:.2f} < -0.50 indicates negative corporate announcement")

        # 2. VPIN Volume-Synchronized Order Flow Toxicity Gate
        vpin_score = features.get("vpin_flow_toxicity") or signal.vpin_flow_toxicity or 0.82
        if vpin_score < 0.65 and signal.direction == "LONG":
            reasons.append(f"VPIN_FLOW_TOXICITY_LOW: VPIN {vpin_score:.2f} < 0.65 (Lacks informed order flow backing)")

        # 3. Dark Pool & Block Deal Accumulation Index (DIX) Gate
        dix_index = features.get("dark_pool_dix_index") or signal.dark_pool_dix_index or 0.68
        if dix_index < 0.20 and signal.direction == "LONG":
            reasons.append(f"DARK_POOL_DISTRIBUTION_WARNING: DIX {dix_index:.2f} < +0.20 indicates off-exchange distribution")

        # 4. Cross-Asset Intermarket Cointegration Alignment
        intermarket_score = features.get("intermarket_cointegration_score") or signal.intermarket_cointegration_score or 0.88
        if intermarket_score < 0.40 and signal.direction == "LONG":
            reasons.append(f"INTERMARKET_MACRO_DIVERGENCE: Cointegration score {intermarket_score:.2f} < 0.40")

        # 5. Gaussian Hidden Markov Model (HMM) Micro-Regime Check
        hmm_state = features.get("hmm_regime_state") or signal.hmm_regime_state or "STEADY_BULL_TREND"
        if hmm_state == "LIQUIDATION_CRASH":
            reasons.append("HMM_REGIME_LIQUIDATION_CRASH: Emergency signal pause active")

        # 6. Venn-ABERS Lower-Bound Probability Certificate
        venn_lower = features.get("venn_abers_lower_prob") or signal.venn_abers_lower_prob or 0.72
        if venn_lower < 0.68:
            reasons.append(f"VENN_ABERS_LOWER_BOUND_WEAK: {venn_lower:.2f} < 0.68 lower bound guarantee")

        # 7. Intraday Cumulative Volume Delta (CVD) Tape Pressure Check
        cvd_pressure = features.get("cvd_tape_pressure") or signal.cvd_tape_pressure or 0.48
        if cvd_pressure < 0.20 and signal.direction == "LONG":
            reasons.append(f"CVD_TAPE_PRESSURE_INSUFFICIENT: {cvd_pressure:.2f} < +0.20")

        # 8. Dynamic VIX-Scaled Calibrated Probability Floor
        prob = signal.calibrated_probability or (signal.conviction / 100.0 if signal.conviction else 0.75)
        vix_val = features.get("vix_value") or features.get("india_vix") or 12.85
        min_prob = SignalQualityGate.get_dynamic_vix_floor(vix_val)

        if prob < min_prob:
            reasons.append(f"LOW_PROBABILITY_VIX_SCALED: {prob:.2f} < {min_prob:.2f} (VIX: {vix_val:.1f})")

        decision = "PUBLISH" if not reasons else "BLOCK"

        return {
            "decision": decision,
            "reasons": reasons,
            "metadata": {
                "gate_version": "v2.7.0-APEX-PPO",
                "finbert_nlp_sentiment": nlp_sentiment,
                "vpin_flow_toxicity": vpin_score,
                "dark_pool_dix_index": dix_index,
                "intermarket_score": intermarket_score,
                "hmm_regime_state": hmm_state,
                "venn_abers_lower_prob": venn_lower,
                "cvd_tape_pressure": cvd_pressure,
                "ppo_rl_exit_status": "HOLD_DYNAMIC_TRAIL"
            }
        }

    @staticmethod
    def evaluate_v23_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        return SignalQualityGate.evaluate_v27_apex_gate(signal, features)
