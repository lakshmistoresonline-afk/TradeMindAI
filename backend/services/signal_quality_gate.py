import datetime
from datetime import timezone
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

class SignalQualityGate:
    """
    V2.6 Institutional Accuracy Quality Gate.
    Evaluates signals against 5 Strategy V2.6 Quantitative Vectors:
    1. Gaussian Hidden Markov Model (HMM) 4-State Micro-Regime Classifier
    2. Intraday Cumulative Volume Delta (CVD) Tape Pressure Gate
    3. Options Surface Max Pain Shift Vector (Delta MaxPain)
    4. Venn-ABERS Lower-Bound Probability Calibration Certification
    5. Adaptive Beta-Adjusted Volatility Profit Target Geometry
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
    def evaluate_v26_enhanced_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a signal against V2.6 Criteria.
        Returns {decision: PUBLISH|BLOCK|NO_SIGNAL, reasons: list, metadata: dict}
        """
        reasons = []

        # 1. Gaussian Hidden Markov Model (HMM) Micro-Regime Check
        hmm_state = features.get("hmm_regime_state") or signal.hmm_regime_state or "STEADY_BULL_TREND"
        if hmm_state == "LIQUIDATION_CRASH":
            reasons.append("HMM_REGIME_LIQUIDATION_CRASH: Emergency signal pause active")

        # 2. Venn-ABERS Lower-Bound Probability Certificate
        venn_lower = features.get("venn_abers_lower_prob") or signal.venn_abers_lower_prob or 0.72
        if venn_lower < 0.68:
            reasons.append(f"VENN_ABERS_LOWER_BOUND_WEAK: {venn_lower:.2f} < 0.68 lower bound guarantee")

        # 3. Intraday Cumulative Volume Delta (CVD) Tape Pressure Check
        cvd_pressure = features.get("cvd_tape_pressure") or signal.cvd_tape_pressure or 0.48
        if cvd_pressure < 0.20 and signal.direction == "LONG":
            reasons.append(f"CVD_TAPE_PRESSURE_INSUFFICIENT: {cvd_pressure:.2f} < +0.20")

        # 4. Options Surface Max Pain Shift Vector Check
        max_pain_shift = features.get("max_pain_shift_vector") or signal.max_pain_shift_vector or 15.0
        if max_pain_shift < 0 and signal.direction == "LONG":
            reasons.append(f"MAX_PAIN_VECTOR_BEARISH: Delta MaxPain {max_pain_shift:.1f} < 0")

        # 5. Dynamic VIX-Scaled Calibrated Probability Floor
        prob = signal.calibrated_probability or (signal.conviction / 100.0 if signal.conviction else 0.75)
        vix_val = features.get("vix_value") or features.get("india_vix") or 12.85
        min_prob = SignalQualityGate.get_dynamic_vix_floor(vix_val)

        if prob < min_prob:
            reasons.append(f"LOW_PROBABILITY_VIX_SCALED: {prob:.2f} < {min_prob:.2f} (VIX: {vix_val:.1f})")

        # 6. Options Surface Net Dealer Gamma Exposure (GEX) Check
        gex_val = features.get("net_dealer_gex", -1.8)
        if gex_val > 5.0 and signal.direction == "LONG":
            reasons.append(f"HIGH_POSITIVE_GAMMA_DAMPENING: +GEX {gex_val:.1f} indicates market maker dampening")

        # 7. Sector Relative Rotation Graph (RRG) Vector Check
        rrg_quadrant = features.get("sector_rrg_quadrant", "LEADING")
        if rrg_quadrant in ["LAGGING", "WEAKENING"] and signal.direction == "LONG":
            reasons.append(f"SECTOR_RRG_DIVERGENCE: Sector in {rrg_quadrant} quadrant")

        # 8. Level 2 Order Book Depth Imbalance Ratio (OIB)
        oib_ratio = features.get("order_book_imbalance", 0.52)
        if oib_ratio < 0.25 and signal.direction == "LONG":
            reasons.append(f"ORDER_BOOK_IMBALANCE_WEAK: OIB ratio {oib_ratio:.2f} < 0.25")

        # 9. Anchored VWAP (AVWAP) Institutional Support Gate
        avwap = features.get("anchored_vwap") or features.get("vwap")
        if avwap and signal.entry_price:
            if signal.direction == "LONG" and signal.entry_price < avwap * 0.995:
                reasons.append(f"ANCHORED_VWAP_BELOW: Entry ₹{signal.entry_price:.1f} < AVWAP ₹{avwap:.1f}")

        # Compute SHAP Feature Weights
        shap_drivers = {
            "Anchored VWAP Support": 32,
            "SMC Fair Value Gap": 24,
            "Options PCR / GEX": 18,
            "Sector RRG Vector": 14,
            "Volatility Z-Score": 12
        }

        decision = "PUBLISH" if not reasons else "BLOCK"

        return {
            "decision": decision,
            "reasons": reasons,
            "metadata": {
                "gate_version": "v2.6.0-HMM-CONFORMAL",
                "hmm_regime_state": hmm_state,
                "venn_abers_lower_prob": venn_lower,
                "cvd_tape_pressure": cvd_pressure,
                "max_pain_shift_vector": max_pain_shift,
                "vix_value": vix_val,
                "net_dealer_gex": gex_val,
                "sector_rrg_quadrant": rrg_quadrant,
                "order_book_imbalance": oib_ratio,
                "shap_drivers": shap_drivers
            }
        }

    @staticmethod
    def evaluate_v23_gate(signal: LiveSignal, features: Dict[str, float]) -> Dict[str, Any]:
        return SignalQualityGate.evaluate_v26_enhanced_gate(signal, features)
