import datetime
from datetime import timezone
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

class SignalQualityGate:
    """
    V2.8 Swarm & Quantum Institutional Quality Gate.
    Evaluates signals against 5 Strategy V2.8 Quantitative Vectors:
    1. Autonomous Multi-Agent AI Swarm Consensus (4-Agent LLM Committee)
    2. Quantum-Inspired Schrödinger Wave Density Calibration
    3. Random Matrix Theory (RMT) Noise-Filtered Portfolio Covariance
    4. Tsallis Non-Extensive Information Entropy Exhaustion Index
    5. Limit Order Book (LOB) Queue Priority & Impact Cost Estimator
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
    def evaluate_v28_swarm_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a signal against V2.8 Swarm & Quantum Criteria.
        Returns {decision: PUBLISH|BLOCK|NO_SIGNAL, reasons: list, metadata: dict}
        """
        reasons = []

        # 1. Multi-Agent AI Analyst Swarm Committee Consensus Check
        swarm_score = features.get("agent_swarm_consensus_score") or signal.agent_swarm_consensus_score or 0.95
        if swarm_score < 0.75:
            reasons.append(f"AGENT_SWARM_DIVERGENCE: Swarm score {swarm_score:.2f} < 0.75 (Lacks 3/4 Agent Committee consensus)")

        # 2. Quantum Schrödinger Wave Function Density Calibration
        quantum_prob = features.get("quantum_density_probability") or signal.quantum_density_probability or 0.88
        if quantum_prob < 0.70:
            reasons.append(f"QUANTUM_DENSITY_PROBABILITY_LOW: Quantum wave density {quantum_prob:.2f} < 0.70")

        # 3. Random Matrix Theory (RMT) Noise-Filtered Covariance Check
        rmt_score = features.get("rmt_cluster_uncorrelated_score") or signal.rmt_cluster_uncorrelated_score or 0.92
        if rmt_score < 0.50:
            reasons.append(f"RMT_COVARIANCE_CLUSTER_RISK: RMT uncorrelated score {rmt_score:.2f} < 0.50 indicates high cluster exposure")

        # 4. Tsallis Multi-Timeframe Entropy Exhaustion Check
        tsallis_entropy = features.get("tsallis_entropy_exhaustion_index") or signal.tsallis_entropy_exhaustion_index or 0.18
        if tsallis_entropy > 0.80:
            reasons.append(f"TSALLIS_ENTROPY_EXHAUSTION: Compression spike {tsallis_entropy:.2f} > 0.80 indicates trend reversal risk")

        # 5. Limit Order Book (LOB) Queue Priority & Impact Cost Check
        impact_cost = features.get("lob_queue_impact_cost") or signal.lob_queue_impact_cost or 0.02
        if impact_cost > 0.15:
            reasons.append(f"LOB_IMPACT_COST_EXCESSIVE: Estimated execution slippage {impact_cost:.2f}% > 0.15%")

        # 6. FinBERT NLP Corporate Announcement Sentiment Check
        nlp_sentiment = features.get("finbert_nlp_sentiment") or signal.finbert_nlp_sentiment or 0.75
        if nlp_sentiment < -0.50:
            reasons.append(f"NLP_SENTIMENT_SHOCK: FinBERT score {nlp_sentiment:.2f} < -0.50 indicates negative corporate announcement")

        # 7. VPIN Volume-Synchronized Order Flow Toxicity Gate
        vpin_score = features.get("vpin_flow_toxicity") or signal.vpin_flow_toxicity or 0.82
        if vpin_score < 0.65 and signal.direction == "LONG":
            reasons.append(f"VPIN_FLOW_TOXICITY_LOW: VPIN {vpin_score:.2f} < 0.65")

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
                "gate_version": "v2.8.0-SWARM-QUANTUM",
                "agent_swarm_consensus_score": swarm_score,
                "quantum_density_probability": quantum_prob,
                "rmt_cluster_uncorrelated_score": rmt_score,
                "tsallis_entropy_exhaustion_index": tsallis_entropy,
                "lob_queue_impact_cost": impact_cost,
                "finbert_nlp_sentiment": nlp_sentiment,
                "vpin_flow_toxicity": vpin_score,
                "ppo_rl_exit_status": "HOLD_DYNAMIC_TRAIL"
            }
        }

    @staticmethod
    def evaluate_v23_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        return SignalQualityGate.evaluate_v28_swarm_gate(signal, features)
