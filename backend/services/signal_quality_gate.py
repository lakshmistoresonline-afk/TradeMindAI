import datetime
from datetime import timezone
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

class SignalQualityGate:
    """
    V2.3 Shadow Quality Gate.
    Implements evidence-driven gating for institutional signals.
    """

    @staticmethod
    def evaluate_v23_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a signal against V2.3 criteria.
        Returns {decision: PUBLISH|BLOCK|NO_SIGNAL, reason: str, metadata: dict}
        """
        reasons = []

        # 1. Calibrated Probability Floor (Validated Forensic Hypothesis)
        prob = signal.calibrated_probability or (signal.conviction / 100.0)
        if prob < settings.V23_MIN_CALIBRATED_PROBABILITY:
            reasons.append(f"LOW_PROBABILITY: {prob:.2f} < {settings.V23_MIN_CALIBRATED_PROBABILITY}")

        # 2. RSI Exhaustion (Experimental Shadow Filter)
        if settings.V23_RSI_EXHAUSTION_ENABLED:
            rsi = features.get("rsi_14") or features.get("RSI")
            if rsi:
                if signal.direction == "LONG" and rsi > settings.V23_RSI_LONG_THRESHOLD:
                    reasons.append(f"RSI_EXHAUSTION_LONG: {rsi:.1f} > {settings.V23_RSI_LONG_THRESHOLD}")
                elif signal.direction == "SHORT" and rsi < settings.V23_RSI_SHORT_THRESHOLD:
                    reasons.append(f"RSI_EXHAUSTION_SHORT: {rsi:.1f} < {settings.V23_RSI_SHORT_THRESHOLD}")

        # 3. Expected Value Gate
        ev = signal.expected_value or 0.0
        if ev <= 0:
            reasons.append(f"NEGATIVE_EXPECTED_VALUE: {ev:.2f}")

        # 4. Risk/Reward Gate
        rr = signal.risk_reward_ratio or 0.0
        if rr < 1.5:
             reasons.append(f"INSUFFICIENT_RR: {rr:.2f}")

        decision = "PUBLISH" if not reasons else "BLOCK"

        return {
            "decision": decision,
            "reasons": reasons,
            "metadata": {
                "gate_version": "v2.3.0",
                "prob_threshold": settings.V23_MIN_CALIBRATED_PROBABILITY,
                "rsi_enabled": settings.V23_RSI_EXHAUSTION_ENABLED,
                "rsi_value": features.get("rsi_14") or features.get("RSI")
            }
        }
